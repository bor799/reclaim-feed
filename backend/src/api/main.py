# -*- coding: utf-8 -*-
"""
FastAPI REST 接口

提供 Pipeline 各阶段的 HTTP 接口，供前端和外部工具调用。
"""

from fastapi import FastAPI, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from ..models import AppConfig, ContentItem, ProviderConfig, BotConfig, EnvironmentConfig
from ..pipeline import Pipeline
from ..outputs.store import ItemStore
from ..config import load_config
from .deps import get_current_user
from ..utils.prompt_manager import get_prompt, update_prompt, get_prompt_history, get_prompt_version
import json
import os
import logging
from pydantic import BaseModel
from typing import Dict, List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
# 使用当前工作目录（Docker WORKDIR /app）作为基准
STATIC_DIR = os.path.join(os.getcwd(), "static")

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
    _scheduler.add_job(
        _pipeline.run,
        'interval',
        hours=6,
        id='periodic_pipeline_run',
        replace_existing=True,
        next_run_time=None # 如果希望立刻执行可以设为 datetime.now()
    )
    _scheduler.start()
    logger.info("后台定时任务 (APScheduler) 已启动，设置为每 6 小时自动萃取一次。")

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
    date: str = None, 
    is_annotated: Optional[bool] = None,
    user_id: str = Depends(get_current_user)
):
    """[MODIFIED] 获取信息流，支持按是否有批注过滤"""
    store = ItemStore(_config)
    
    # 模拟多租户：原本 store.get_all() 可以过滤 user_id
    if date:
        items = store.get_by_date(date)
    else:
        items = store.get_all()
        
    if is_annotated is not None:
        items = [
            i for i in items 
            if bool(i.get("is_annotated") or i.get("annotation")) == is_annotated
        ]
        
    return items


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
async def get_sources(user_id: str = Depends(get_current_user)):
    """[MODIFIED] 返回含 cron_interval 与 default_tags 的 Source"""
    return [s.model_dump() for s in _config.sources if getattr(s, 'user_id', 'local_admin') == user_id]


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


@app.get("/api/v1/prompts/{stage}")
async def get_prompt_api(stage: str, user_id: str = Depends(get_current_user)):
    """[NEW] 读取指定阶段 Prompt"""
    content = get_prompt(stage)
    if content is None:
        return {"status": "error", "message": f"Stage {stage} not found or prompt empty"}
    history = get_prompt_history(stage)
    return {"content": content, "history": history}


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
