# -*- coding: utf-8 -*-
"""
FastAPI REST 接口

提供 Pipeline 各阶段的 HTTP 接口，供前端和外部工具调用。
"""

from fastapi import FastAPI, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from ..models import (
    AppConfig, ContentItem, ProviderConfig, BotConfig, EnvironmentConfig,
    FeedUpdateRequest, SourceBulkRequest, SourceBulkStatusRequest, 
    PromptVersionRestoreRequest, TestConnectionRequest
)
from ..pipeline import Pipeline
from ..outputs.store import ItemStore
from ..config import load_config
from .deps import get_current_user
from ..utils.prompt_manager import get_prompt, update_prompt, get_prompt_history, get_prompt_version
import json
import os
import logging
import time
import httpx
from pydantic import BaseModel
from typing import Dict, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Query
from fastapi.responses import Response

logger = logging.getLogger(__name__)

class TagsUpdate(BaseModel):
    categories: Dict[str, List[str]]

class QuickExtractRequest(BaseModel):
    urls: List[str]

class PromptUpdateRequest(BaseModel):
    content: str

app = FastAPI(
    title="100X Knowledge Agent",
    description="做深不做宽 — AI 深度知识萃取 API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取静态文件目录路径（用于部署时挂载前端构建产物）
# 从 backend/src/api/main.py 向上三级到项目根目录，然后访问 static/
# __file__ = /app/src/api/main.py
# dirname x 3 = /app
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_CURRENT_DIR))
STATIC_DIR = os.path.join(_PROJECT_ROOT, "static")

# 挂载静态文件
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

# 全局配置与调度器（启动时加载）
_config: AppConfig = None
_pipeline: Pipeline = None
_scheduler: AsyncIOScheduler = None


@app.on_event("startup")
async def startup():
    global _config, _pipeline, _scheduler
    _config = load_config()
    _pipeline = Pipeline(_config)
    
    # 启动后台定时任务
    _scheduler = AsyncIOScheduler()
    
    # 根据源独立挂载任务
    for source in _config.sources:
        if source.enabled and source.cron_interval:
            interval_kwargs = {}
            interval_str = source.cron_interval.lower()
            if interval_str.endswith("h"):
                interval_kwargs['hours'] = int(interval_str[:-1])
            elif interval_str.endswith("m"):
                interval_kwargs['minutes'] = int(interval_str[:-1])
            elif interval_str == "daily":
                interval_kwargs['days'] = 1
            else:
                interval_kwargs['hours'] = 6 # fallback

            _scheduler.add_job(
                _pipeline.run,
                'interval',
                **interval_kwargs,
                id=f'pipeline_run_{source.name}',
                replace_existing=True,
                kwargs={"source_name": source.name}
            )

    # 兜底：如果没有任何源配了 cron_interval，还是挂一个默认的？
    # 取决于需求，目前按文档要求各自独立挂载。
    if not _scheduler.get_jobs():
        logger.info("没有检测到任何具有 cron_interval 的源，未注册定时任务。")

    _scheduler.start()
    logger.info("后台定时任务 (APScheduler) 已根据配置独立启动。")

@app.on_event("shutdown")
async def shutdown():
    if _scheduler:
        _scheduler.shutdown()
        logger.info("后台定时任务 (APScheduler) 已关闭。")

# ──────────────────────────────────────────────
# 核心接口
# ──────────────────────────────────────────────

# =====================================================================
# API - Module 1: Unified Workspace
# =====================================================================

@app.post("/api/v1/run")
async def run_pipeline(
    background_tasks: BackgroundTasks, 
    dry_run: bool = False,
    user_id: str = Depends(get_current_user)
):
    """触发完整 Pipeline"""
    background_tasks.add_task(_pipeline.run, dry_run=dry_run)
    return {"status": "started", "message": "Pipeline 已在后台启动"}


@app.get("/api/v1/user/stats")
async def get_user_stats(user_id: str = Depends(get_current_user)):
    """[NEW] 返回当前用户数据看板"""
    store = ItemStore(_config)
    items = store.get_all()
    
    total_notes = len(items)
    annotations_count = sum(1 for i in items if i.get("is_annotated") or i.get("annotation"))
    
    # 算总天数（简化版：按已知项目的第一条时间计算，或假定加入10天）
    # 算总标签：去重
    total_tags_set = set()
    for item in items:
        total_tags_set.update(item.get("tags", []))

    return {
        "user_id": user_id,
        "total_notes": total_notes,
        "total_tags": len(total_tags_set),
        "days_active": 30, # TODO: 从数据库 user 实体读取
        "annotations_count": annotations_count
    }


@app.get("/api/v1/feed")
async def get_feed(
    page: int = 1,
    limit: int = 50,
    search_query: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date: Optional[str] = None, 
    is_favorited: Optional[bool] = None,
    is_read: Optional[bool] = None,
    is_annotated: Optional[bool] = None,
    user_id: str = Depends(get_current_user)
):
    """[MODIFIED] 升级为 Unified Timeline API，支持多重过滤与智能排序"""
    store = ItemStore(_config)
    
    # 1. 高级搜索与过滤
    items = store.search(
        user_id=user_id,
        search_query=search_query,
        tags=tags,
        start_date=start_date,
        end_date=end_date,
        date=date,
        is_favorited=is_favorited,
        is_read=is_read,
        is_annotated=is_annotated
    )
        
    # 2. 混合排序：先按到达时间倒序
    def get_time(item):
        return item.get("published_at") or item.get("created_at") or ""

    items.sort(key=get_time, reverse=True)
    
    # 3. 未读优先强制置顶 (抖音引力流体验)
    # is_read 为 False 往前排, is_read 为 True 往后排
    items.sort(key=lambda x: 1 if x.get("is_read", False) else 0)
    
    # 4. 分页下发
    start = (page - 1) * limit
    end = start + limit
    paginated_items = items[start:end]
    
    return {
        "items": paginated_items,
        "total": len(items),
        "page": page,
        "limit": limit,
        "has_more": end < len(items)
    }


@app.put("/api/v1/feed/{item_id}")
async def update_feed_item(
    item_id: str,
    req: FeedUpdateRequest,
    user_id: str = Depends(get_current_user)
):
    """[NEW] 修改单条 Feed 卡片（编辑或打标签）"""
    store = ItemStore(_config)
    updates = req.model_dump(exclude_unset=True)
    updated_item = store.update_item(item_id, updates)
    if not updated_item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "item": updated_item}


@app.put("/api/v1/feed/{item_id}/read")
async def mark_feed_read(item_id: str, user_id: str = Depends(get_current_user)):
    """[NEW] 标记卡片已读"""
    store = ItemStore(_config)
    updated_item = store.update_item(item_id, {"is_read": True})
    if not updated_item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "is_read": True}


@app.put("/api/v1/feed/{item_id}/like")
async def toggle_feed_like(item_id: str, user_id: str = Depends(get_current_user)):
    """[NEW] 翻转卡片 Favorite 状态"""
    store = ItemStore(_config)
    item = store.get_by_id(item_id)
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    
    new_state = not item.get("is_favorited", False)
    updated_item = store.update_item(item_id, {"is_favorited": new_state})
    return {"status": "success", "is_favorited": new_state}


@app.get("/api/v1/export/feed")
async def export_feed_csv(
    search_query: Optional[str] = None,
    tags: Optional[List[str]] = Query(default=None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date: Optional[str] = None, 
    is_favorited: Optional[bool] = None,
    is_read: Optional[bool] = None,
    is_annotated: Optional[bool] = None,
    user_id: str = Depends(get_current_user)
):
    """[NEW] 根据当前过滤条件导出 Feed 数据（CSV格式）"""
    store = ItemStore(_config)
    items = store.search(
        user_id=user_id,
        search_query=search_query,
        tags=tags,
        start_date=start_date,
        end_date=end_date,
        date=date,
        is_favorited=is_favorited,
        is_read=is_read,
        is_annotated=is_annotated
    )
    
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "URL", "Source", "Date", "Content Snippet", "Tags", "My Annotation", "Is Read", "Is Favorited"])
    
    for i in items:
        writer.writerow([
            i.get("title", ""),
            i.get("url", ""),
            i.get("source", ""),
            i.get("published_at") or i.get("created_at"),
            (i.get("content", "")[:200]).replace("\n", " "),
            ",".join(i.get("tags", [])),
            i.get("annotation", ""),
            i.get("is_read", False),
            i.get("is_favorited", False)
        ])
    
    csv_str = output.getvalue()
    return Response(
        content=csv_str, 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=feed_export.csv"}
    )


@app.post("/api/v1/extract/quick")
async def quick_extract(
    req: QuickExtractRequest, 
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """[NEW] 旁路加速萃取接口"""
    # 1. 包装为假想的临时 Items
    dummy_items = [
        ContentItem(
            user_id=user_id,
            title=f"Quick Extract: {url[:30]}",
            url=url,
            source_detail=url,
            content="[Data will be fetched during pipeline run...]" # 模拟：需单独调用爬虫逻辑
        ) for url in req.urls
    ]
    
    # 因为真实的 Pipeline.run() 是全量抓取。这里我们模拟独立处理管道。
    # 实际开发中应调用底层的单条处理逻辑
    # 暂时由 background_tasks 执行并返回 202
    
    async def process_quick(items):
        passed = await _pipeline.filter(items)
        analyzed = await _pipeline.analyze(passed)
        await _pipeline.output(analyzed)
        
    background_tasks.add_task(process_quick, dummy_items)
    return {"status": "processing", "message": f"{len(req.urls)} URLs submitted to queue."}


@app.get("/api/v1/tags")
async def get_tags(user_id: str = Depends(get_current_user)):
    """获取所有全局标签"""
    tags_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "prompts", "tags.json")
    if not os.path.exists(tags_file):
        return {"categories": {}}
    with open(tags_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.put("/api/v1/tags")
async def update_tags(tags_data: TagsUpdate, user_id: str = Depends(get_current_user)):
    tags_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "prompts", "tags.json")
    os.makedirs(os.path.dirname(tags_file), exist_ok=True)
    with open(tags_file, "w", encoding="utf-8") as f:
        json.dump(tags_data.model_dump(), f, ensure_ascii=False, indent=2)
    return {"status": "success"}


# =====================================================================
# API - Module 2: Workflow & Sources
# =====================================================================

@app.get("/api/v1/sources")
async def get_sources(
    status: Optional[str] = None, 
    tag: Optional[str] = None, 
    search_query: Optional[str] = None,
    user_id: str = Depends(get_current_user)
):
    """[MODIFIED] 返回含 cron_interval 与 default_tags 的 Source，并支持高级过滤"""
    sources = [s.model_dump() for s in _config.sources if getattr(s, 'user_id', 'local_admin') == user_id]
    
    if status is not None:
        is_enabled = status.lower() in ("active", "enabled", "true", "1")
        sources = [s for s in sources if s.get("enabled", False) == is_enabled]
        
    if tag:
        sources = [s for s in sources if tag in s.get("default_tags", []) or tag == s.get("category")]
        
    if search_query:
        q = search_query.lower()
        sources = [s for s in sources if q in s.get("name", "").lower() or q in s.get("url", "").lower()]
        
    return sources


@app.post("/api/v1/sources")
async def add_source(source: dict, user_id: str = Depends(get_current_user)):
    from ..models import SourceConfig
    source["user_id"] = user_id
    new_source = SourceConfig(**source)
    _config.sources.append(new_source)
    _save_config()
    return {"status": "success", "source": new_source.model_dump()}


@app.put("/api/v1/sources/{source_index}")
async def update_source(source_index: int, source: dict, user_id: str = Depends(get_current_user)):
    if 0 <= source_index < len(_config.sources):
        from ..models import SourceConfig
        source["user_id"] = user_id
        _config.sources[source_index] = SourceConfig(**source)
        _save_config()
        return {"status": "success"}
    return {"status": "error", "message": "Source not found"}


@app.delete("/api/v1/sources/{source_index}")
async def delete_source(source_index: int, user_id: str = Depends(get_current_user)):
    if 0 <= source_index < len(_config.sources):
        _config.sources.pop(source_index)
        _save_config()
        return {"status": "success"}
    return {"status": "error", "message": "Source not found"}


@app.delete("/api/v1/sources/bulk")
async def delete_sources_bulk(req: SourceBulkRequest, user_id: str = Depends(get_current_user)):
    """[NEW] 批量删除 Source"""
    # 倒序删除避免索引越界
    for idx in sorted(req.ids, reverse=True):
        if 0 <= idx < len(_config.sources):
            _config.sources.pop(idx)
    _save_config()
    return {"status": "success"}


@app.put("/api/v1/sources/bulk/status")
async def update_sources_bulk_status(req: SourceBulkStatusRequest, user_id: str = Depends(get_current_user)):
    """[NEW] 批量更新 Source 启用状态"""
    for idx in set(req.ids):
        if 0 <= idx < len(_config.sources):
            _config.sources[idx].enabled = req.enabled
    _save_config()
    return {"status": "success"}


@app.get("/api/v1/prompts/{stage}")
async def get_prompt_api(stage: str, user_id: str = Depends(get_current_user)):
    """读取指定阶段 Prompt 的当前版本和基本历史"""
    content = get_prompt(stage)
    if content is None:
        return {"status": "error", "message": f"Stage {stage} not found or prompt empty"}
    history = get_prompt_history(stage)
    return {"content": content, "history": history}


@app.get("/api/v1/prompts/{stage}/versions")
async def get_prompt_versions_api(stage: str, user_id: str = Depends(get_current_user)):
    """[NEW] 获取某阶段的所有历史版本清单"""
    try:
        history = get_prompt_history(stage)
        return {"status": "success", "versions": history}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/v1/prompts/{stage}/versions")
async def restore_prompt_version_api(stage: str, req: PromptVersionRestoreRequest, user_id: str = Depends(get_current_user)):
    """[NEW] 恢复到指定的 Prompt 版本"""
    try:
        old_content = get_prompt_version(stage, req.version)
        if not old_content:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Version not found")
        
        # 将老版本内容写回到当前，同时在内部作为一次新修改（会产生新的当前版）
        update_prompt(stage, old_content)
        return {"status": "success", "content": old_content}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.put("/api/v1/prompts/{stage}")
async def update_prompt_api(stage: str, req: PromptUpdateRequest, user_id: str = Depends(get_current_user)):
    """[NEW] 更新指定阶段 Prompt 并归档旧版本"""
    try:
        result = update_prompt(stage, req.content)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =====================================================================
# API - Module 3: Settings
# =====================================================================

@app.get("/api/v1/settings")
async def get_all_settings(user_id: str = Depends(get_current_user)):
    """获取所有配置概览"""
    return _config.model_dump(exclude={"llm": {"api_key_env"}})


@app.get("/api/v1/settings/providers")
async def get_providers(user_id: str = Depends(get_current_user)):
    """[NEW] 获取大模型服务商"""
    return [p.model_dump() for p in _config.providers]


@app.put("/api/v1/settings/providers")
async def update_providers(providers: List[ProviderConfig], user_id: str = Depends(get_current_user)):
    """[NEW] 更新大模型服务商"""
    _config.providers = providers
    _save_config()
    return {"status": "success"}


@app.get("/api/v1/settings/bots")
async def get_bots(user_id: str = Depends(get_current_user)):
    """[NEW] 获取 Bot 频道配置"""
    return _config.bots.model_dump()


@app.put("/api/v1/settings/bots")
async def update_bots(bots: BotConfig, user_id: str = Depends(get_current_user)):
    """[NEW] 更新 Bot 频道配置"""
    _config.bots = bots
    _save_config()
    return {"status": "success"}


@app.get("/api/v1/settings/environment")
async def get_environment(user_id: str = Depends(get_current_user)):
    """[NEW] 获取系统环境偏好"""
    return _config.environment.model_dump()


@app.put("/api/v1/settings/environment")
async def update_environment(env: EnvironmentConfig, user_id: str = Depends(get_current_user)):
    """[NEW] 设置系统环境偏好"""
    _config.environment = env
    _save_config()
    return {"status": "success"}


@app.post("/api/v1/system/test-connection")
async def test_connection(req: TestConnectionRequest, user_id: str = Depends(get_current_user)):
    """[NEW] 连通性测试 API (支持代理)"""
    # 查找 Provider
    provider_name = req.provider_name or _config.llm.provider
    provider = next((p for p in _config.providers if p.name.lower() == provider_name.lower()), None)
    
    if not provider:
        # Fallback to default llm mapping if provider entry doesn't exist yet but user wants to test
        api_key = os.environ.get(_config.llm.api_key_env, "")
        api_base = _config.llm.api_base
        proxy_url = None
    else:
        api_key = provider.api_key
        api_base = provider.api_base
        proxy_url = getattr(provider, "proxy_url", None)
        
    start_time = time.time()
    try:
        # Construct testing client
        transport = None
        if proxy_url:
            from httpx_socks import AsyncProxyTransport
            if proxy_url.startswith("socks"):
                transport = AsyncProxyTransport.from_url(proxy_url)
                
        # Simple HTTP probe to the models endpoint (standard for OpenAI compatibles including DeepSeek/Zhipu/etc)
        # We only send an OPTIONS/GET to check ping speed
        probe_url = api_base.rstrip("/") + "/models" if "openai" in api_base.lower() or "deepseek" in api_base.lower() or "zhipu" in api_base.lower() else api_base
        
        async with httpx.AsyncClient(transport=transport, timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            # Some non-openai endpoints might fail on /models, so we gracefully catch 404s and just measure connection
            response = await client.get(probe_url, headers=headers)
            
        latency = int((time.time() - start_time) * 1000)
        
        if response.status_code in (200, 401, 403, 404, 405): # Connect success, Auth might fail, but connection is OK
            success = response.status_code == 200
            error = f"Auth/Endpoint error (HTTP {response.status_code})" if not success else None
            return {
                "success": success,
                "latency_ms": latency,
                "error": error
            }
        else:
            return {
                "success": False,
                "latency_ms": latency,
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "latency_ms": latency,
            "error": str(e)
        }


# =====================================================================
# Core Utils & Health
# =====================================================================

def _save_config():
    import yaml
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "config.yaml")
    if not os.path.exists(config_file):
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "config.example.yaml")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    data['sources'] = [s.model_dump(exclude_unset=True) for s in _config.sources]
    data['providers'] = [p.model_dump(exclude_unset=True) for p in _config.providers]
    data['bots'] = _config.bots.model_dump(exclude_unset=True)
    data['environment'] = _config.environment.model_dump(exclude_unset=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "multi_tenant": True}


# ──────────────────────────────────────────────
# 导出接口（预留）
# ──────────────────────────────────────────────

@app.get("/api/v1/export/markdown")
async def export_markdown(user_id: str = Depends(get_current_user)):
    """导出 Markdown 格式"""
    # TODO: Phase 2
    return {"status": "not_implemented"}


@app.get("/api/v1/export/json")
async def export_json(user_id: str = Depends(get_current_user)):
    """导出 JSON 格式"""
    store = ItemStore(_config)
    return store.get_all()


# ──────────────────────────────────────────────
# SPA Fallback (用于部署时服务前端)
# ──────────────────────────────────────────────

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """SPA fallback: 对于非 API 请求，返回 index.html"""
    # 如果是 API 请求，返回 404
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # 返回 index.html 以支持 React Router
    if os.path.exists(STATIC_DIR):
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Frontend not built")
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Frontend not built")


# ──────────────────────────────────────────────
# 启动入口
# ──────────────────────────────────────────────

def start_server(config: AppConfig = None, host: str = "0.0.0.0", port: int = None):
    """启动 FastAPI 服务"""
    import uvicorn
    import os

    # 优先使用环境变量 PORT，其次使用传入参数，最后使用默认值
    if port is None:
        port = int(os.getenv("PORT", "8000"))

    if config:
        global _config, _pipeline
        _config = config
        _pipeline = Pipeline(config)
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
