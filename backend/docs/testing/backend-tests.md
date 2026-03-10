# Backend Tests - 100X Knowledge Agent

## 测试概览 (Test Overview)

本后端测试套件使用 **pytest** 框架，覆盖了数据模型、API 端点、集成场景和边界情况。

**框架**: pytest 9.0.2
**总测试数**: 150
**通过率**: 100%
**覆盖率**: 71%

---

## 测试模块说明 (Test Modules)

### 1. test_models.py (50 tests)

数据模型的单元测试，确保 Pydantic 模型的正确性。

#### TestContentItem (7 tests)
- `test_content_item_creation_minimal` - 最小字段创建测试
- `test_content_item_creation_full` - 完整字段创建测试
- `test_content_item_enum_defaults` - 枚举默认值测试
- `test_content_item_lists_default_empty` - 列表字段默认空值测试
- `test_content_item_optional_fields` - 可选字段测试
- `test_content_item_with_user_notes` - 用户笔记测试
- `test_content_item_extraction_dict` - 萃取字典测试

#### TestSourceConfig (6 tests)
- `test_source_config_minimal` - 最小配置测试
- `test_source_config_full` - 完整配置测试
- `test_source_config_all_types` - 所有源类型测试
- `test_source_config_tags_default` - 标签默认值测试
- `test_source_config_extra_default` - 额外字段默认值测试

#### TestAppConfig (5 tests)
- `test_app_config_default` - 默认配置测试
- `test_app_config_with_llm` - LLM 配置测试
- `test_app_config_with_providers` - 多提供商配置测试
- `test_app_config_with_sources` - 多源配置测试
- `test_app_config_with_bots` - Bot 配置测试
- `test_app_config_with_environment` - 环境配置测试

#### TestFilterConfig (2 tests)
- `test_filter_config_defaults` - 默认值测试
- `test_filter_config_custom` - 自定义值测试

#### TestExtractionConfig (2 tests)
- `test_extraction_config_defaults` - 默认值测试
- `test_extraction_config_custom` - 自定义值测试

#### TestOutputConfig (2 tests)
- `test_output_config_defaults` - 默认值测试
- `test_output_config_custom` - 自定义值测试

#### TestLLMConfig (2 tests)
- `test_llm_config_defaults` - 默认值测试
- `test_llm_config_custom` - 自定义值测试

#### TestProviderConfig (3 tests)
- `test_provider_config_minimal` - 最小配置测试
- `test_provider_config_full` - 完整配置测试
- `test_provider_config_optional_proxy` - 可选代理测试

#### TestBotConfig (3 tests)
- `test_bot_config_defaults` - 默认值测试
- `test_bot_config_telegram` - Telegram 配置测试
- `test_bot_config_feishu` - 飞书配置测试

#### TestEnvironmentConfig (2 tests)
- `test_environment_config_defaults` - 默认值测试
- `test_environment_config_custom` - 自定义值测试

#### TestRequestModels (7 tests)
- `test_feed_update_request_minimal` - 最小更新请求测试
- `test_feed_update_request_partial` - 部分更新测试
- `test_feed_update_request_full` - 完整更新测试
- `test_source_bulk_request` - 批量源请求测试
- `test_source_bulk_status_request` - 批量状态请求测试
- `test_prompt_version_restore_request` - 版本恢复请求测试
- `test_test_connection_request_default` - 连接测试默认值测试
- `test_test_connection_request_with_provider` - 连接测试指定提供商测试

#### TestUserStats (2 tests)
- `test_user_stats_defaults` - 默认值测试
- `test_user_stats_with_values` - 带值测试

#### TestEnums (3 tests)
- `test_source_type_values` - 源类型枚举测试
- `test_item_status_values` - 项目状态枚举测试
- `test_decision_values` - 决策枚举测试

#### TestModelValidation (3 tests)
- `test_content_item_url_validation` - URL 验证测试
- `test_multiple_tags` - 多标签测试
- `test_reread_worthy_flag` - 重读标志测试

---

### 2. test_api.py (8 tests)

基础 API 端点测试。

| 测试 | 端点 | 说明 |
|------|------|------|
| `test_health` | GET /api/v1/health | 健康检查 |
| `test_user_stats` | GET /api/v1/user/stats | 用户统计 |
| `test_get_feed` | GET /api/v1/feed | 获取 Feed |
| `test_get_sources` | GET /api/v1/sources | 获取源列表 |
| `test_add_source` | POST /api/v1/sources | 添加源 |
| `test_get_settings_providers` | GET /api/v1/settings/providers | 获取 LLM 提供商 |
| `test_test_connection_no_provider` | POST /api/v1/system/test-connection | 测试连接（无提供商） |
| `test_quick_extract` | POST /api/v1/extract/quick | 快速萃取 |

---

### 3. test_feed_api.py (29 tests)

Feed API 端点测试，包含基础测试、集成测试和边界测试。

#### TestFeedAPI (21 tests)
| 测试 | 端点 | 说明 |
|------|------|------|
| `test_feed_basic` | GET /api/v1/feed | 基础 Feed 获取 |
| `test_feed_pagination` | GET /api/v1/feed?page=1&limit=10 | 分页测试 |
| `test_feed_search_query` | GET /api/v1/feed?search_query=AI | 搜索查询过滤 |
| `test_feed_tags_filter` | GET /api/v1/feed?tags=AI&tags=ML | 标签过滤 |
| `test_feed_date_filter` | GET /api/v1/feed?date=2026-03-10 | 日期过滤 |
| `test_feed_date_range_filter` | GET /api/v1/feed?start_date=...&end_date=... | 日期范围过滤 |
| `test_feed_favorited_filter` | GET /api/v1/feed?is_favorited=true | 收藏过滤 |
| `test_feed_read_filter` | GET /api/v1/feed?is_read=true | 已读过滤 |
| `test_feed_annotated_filter` | GET /api/v1/feed?is_annotated=true | 注释过滤 |
| `test_feed_combined_filters` | GET /api/v1/feed?search=...&tags=... | 组合过滤 |
| `test_feed_unread_priority` | GET /api/v1/feed?limit=50 | 未读优先级测试 |
| `test_update_feed_item` | PUT /api/v1/feed/{id} | 更新 Feed 项目 |
| `test_mark_feed_read` | PUT /api/v1/feed/{id}/read | 标记已读 |
| `test_toggle_feed_like` | PUT /api/v1/feed/{id}/like | 切换收藏 |
| `test_export_feed_csv` | GET /api/v1/export/feed | CSV 导出 |
| `test_export_feed_csv_with_filters` | GET /api/v1/export/feed?... | 带过滤导出 |
| `test_quick_extract_single` | POST /api/v1/extract/quick | 单 URL 萃取 |
| `test_quick_extract_multiple` | POST /api/v1/extract/quick | 多 URL 萃取 |
| `test_quick_extract_empty_urls` | POST /api/v1/extract/quick | 空 URL 列表 |
| `test_get_tags` | GET /api/v1/tags | 获取标签 |
| `test_update_tags` | PUT /api/v1/tags | 更新标签 |
| `test_user_stats` | GET /api/v1/user/stats | 用户统计 |

#### TestFeedAPIIntegration (2 tests)
| 测试 | 说明 |
|------|------|
| `test_feed_workflow` | 完整 Feed 工作流：获取 → 更新 → 导出 |
| `test_search_and_export_workflow` | 搜索和导出工作流 |

#### TestFeedAPIEdgeCases (6 tests)
| 测试 | 说明 |
|------|------|
| `test_feed_large_limit` | 大 limit 测试 |
| `test_feed_zero_limit` | 零 limit 测试 |
| `test_feed_negative_page` | 负页码测试 |
| `test_feed_special_characters_search` | 特殊字符搜索 |
| `test_feed_unicode_tags` | Unicode 标签 |

---

### 4. test_settings_api.py (30 tests)

Settings API 端点测试。

#### TestSettingsAPI (19 tests)
| 测试 | 端点 | 说明 |
|------|------|------|
| `test_get_all_settings` | GET /api/v1/settings | 获取所有设置 |
| `test_get_providers` | GET /api/v1/settings/providers | 获取提供商 |
| `test_get_providers_empty` | GET /api/v1/settings/providers | 空提供商列表 |
| `test_update_providers` | PUT /api/v1/settings/providers | 更新提供商 |
| `test_update_providers_empty` | PUT /api/v1/settings/providers | 空提供商更新 |
| `test_update_providers_with_proxy` | PUT /api/v1/settings/providers | 带代理更新 |
| `test_get_bots` | GET /api/v1/settings/bots | 获取 Bot 配置 |
| `test_get_bots_empty` | GET /api/v1/settings/bots | 空 Bot 配置 |
| `test_update_bots` | PUT /api/v1/settings/bots | 更新 Bot 配置 |
| `test_update_bots_partial` | PUT /api/v1/settings/bots | 部分更新 |
| `test_get_environment` | GET /api/v1/settings/environment | 获取环境设置 |
| `test_update_environment` | PUT /api/v1/settings/environment | 更新环境设置 |
| `test_update_environment_locale` | PUT /api/v1/settings/environment | 更新语言 |
| `test_test_connection_default_provider` | POST /api/v1/system/test-connection | 默认提供商连接测试 |
| `test_test_connection_named_provider` | POST /api/v1/system/test-connection | 指定提供商连接测试 |
| `test_test_connection_nonexistent_provider` | POST /api/v1/system/test-connection | 不存在的提供商 |
| `test_test_connection_with_proxy` | POST /api/v1/system/test-connection | 带代理连接测试 |
| `test_export_json` | GET /api/v1/export/json | JSON 导出 |
| `test_export_markdown` | GET /api/v1/export/markdown | Markdown 导出 |

#### TestSettingsAPIIntegration (3 tests)
| 测试 | 说明 |
|------|------|
| `test_settings_workflow` | 设置工作流：获取 → 更新 → 验证 |
| `test_provider_connection_workflow` | 提供商连接工作流 |
| `test_export_multiple_formats` | 多格式导出 |

#### TestSettingsAPIEdgeCases (5 tests)
| 测试 | 说明 |
|------|------|
| `test_providers_with_special_characters` | 特殊字符提供商名 |
| `test_environment_with_path_traversal` | 路径遍历尝试 |
| `test_bots_with_invalid_tokens` | 无效 token 格式 |
| `test_multiple_providers_same_name` | 重复提供商名 |
| `test_connection_timeout_handling` | 连接超时处理 |

#### TestRunPipelineAPI (3 tests)
| 测试 | 端点 | 说明 |
|------|------|------|
| `test_run_pipeline_dry_run` | POST /api/v1/run?dry_run=true | 干运行模式 |
| `test_run_pipeline_normal` | POST /api/v1/run | 正常运行 |
| `test_run_pipeline_multiple_times` | POST /api/v1/run | 多次运行 |

---

### 5. test_sources_api.py (33 tests)

Sources API 端点测试。

#### TestSourcesAPI (17 tests)
| 测试 | 端点 | 说明 |
|------|------|------|
| `test_get_sources_basic` | GET /api/v1/sources | 基础获取 |
| `test_get_sources_with_status_filter` | GET /api/v1/sources?status=active | 状态过滤 |
| `test_get_sources_with_tag_filter` | GET /api/v1/sources?tag=AI | 标签过滤 |
| `test_get_sources_with_search_query` | GET /api/v1/sources?search_query=test | 搜索查询 |
| `test_get_sources_combined_filters` | GET /api/v1/sources?... | 组合过滤 |
| `test_add_source_minimal` | POST /api/v1/sources | 最小添加 |
| `test_add_source_full` | POST /api/v1/sources | 完整添加 |
| `test_add_source_all_types` | POST /api/v1/sources | 所有源类型 |
| `test_add_source_invalid_type` | POST /api/v1/sources | 无效类型 |
| `test_update_source` | PUT /api/v1/sources/0 | 更新源 |
| `test_update_source_invalid_index` | PUT /api/v1/sources/999 | 无效索引 |
| `test_delete_source` | DELETE /api/v1/sources/0 | 删除源 |
| `test_delete_source_invalid_index` | DELETE /api/v1/sources/999 | 无效索引删除 |
| `test_delete_sources_bulk` | DELETE /api/v1/sources/bulk | 批量删除 |
| `test_delete_sources_bulk_empty` | DELETE /api/v1/sources/bulk | 空批量删除 |
| `test_update_sources_bulk_status_enable` | PUT /api/v1/sources/bulk/status | 批量启用 |
| `test_update_sources_bulk_status_disable` | PUT /api/v1/sources/bulk/status | 批量禁用 |
| `test_update_sources_bulk_status_empty` | PUT /api/v1/sources/bulk/status | 空批量状态 |

#### TestPromptsAPI (8 tests)
| 测试 | 端点 | 说明 |
|------|------|------|
| `test_get_prompt_scoring` | GET /api/v1/prompts/scoring | 获取评分提示词 |
| `test_get_prompt_extraction` | GET /api/v1/prompts/extraction | 获取萃取提示词 |
| `test_get_prompt_invalid_stage` | GET /api/v1/prompts/invalid_stage | 无效阶段 |
| `test_get_prompt_versions` | GET /api/v1/prompts/scoring/versions | 获取版本 |
| `test_restore_prompt_version` | POST /api/v1/prompts/scoring/versions | 恢复版本 |
| `test_restore_prompt_invalid_version` | POST /api/v1/prompts/scoring/versions | 无效版本 |
| `test_update_prompt` | PUT /api/v1/prompts/scoring | 更新提示词 |
| `test_update_prompt_empty` | PUT /api/v1/prompts/scoring | 空提示词 |

#### TestSourcesAPIIntegration (2 tests)
| 测试 | 说明 |
|------|------|
| `test_source_lifecycle` | 源生命周期：添加 → 获取 → 更新 → 删除 |
| `test_prompt_workflow` | 提示词工作流：获取 → 更新 → 恢复版本 |

#### TestSourcesAPIEdgeCases (6 tests)
| 测试 | 说明 |
|------|------|
| `test_sources_with_unicode_name` | Unicode 源名称 |
| `test_sources_very_long_url` | 超长 URL |
| `test_cron_intervals` | 各种 cron 间隔格式 |
| `test_bulk_operations_with_duplicates` | 重复 ID 批量操作 |
| `test_negative_source_index` | 负索引操作 |

---

## 测试分层结构 (Test Layering)

```
┌─────────────────────────────────────────┐
│         Integration Tests               │  工作流测试
│  (Multi-step workflows)                 │
├─────────────────────────────────────────┤
│           API Tests                     │  端点测试
│  (HTTP endpoints, requests/responses)   │
├─────────────────────────────────────────┤
│         Unit Tests                      │  单元测试
│  (Models, schemas, validation)          │
├─────────────────────────────────────────┤
│         Edge Cases                      │  边界测试
│  (Boundary conditions, errors)          │
└─────────────────────────────────────────┘
```

---

## 运行测试 (Running Tests)

### 本地开发

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source .venv/bin/activate

# 运行所有测试
pytest tests/ -v

# 运行特定文件
pytest tests/test_models.py -v

# 运行特定测试类
pytest tests/test_feed_api.py::TestFeedAPI -v

# 运行特定测试
pytest tests/test_models.py::TestContentItem::test_content_item_creation_minimal -v

# 带覆盖率运行
pytest tests/ --cov=src --cov-report=html

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=term-missing
```

### CI/CD 集成

测试在以下情况下自动运行：
- Pull Request 创建/更新
- Push 到 main 分支
- Release 前检查

---

## 测试数据说明 (Test Data)

### Mock Data Fixtures

**mock_feed_items** - 模拟 Feed 数据：
- 4 个模拟内容项
- 包含不同状态：未读、已读、收藏、边缘情况
- 质量分数：4.0 - 8.5
- 决策类型：通过、边缘、拒绝

**mock_sources** - 模拟源数据：
- 3 个模拟源配置
- 类型：RSS、IMPORT
- 不同 cron 间隔

### Test Config

测试使用独立的配置，通过 `monkeypatch` 模拟：
- 临时目录存储
- 空的 items.json 存储
- 测试用户认证覆盖

---

## 已知问题和警告 (Known Issues)

### Deprecation Warnings

1. **Pydantic ConfigDict**: ContentItem 使用旧式 `Config` 类
   - 计划迁移到 `ConfigDict`

2. **FastAPI on_event**: 使用已弃用的 `@app.on_event` 装饰器
   - 计划迁移到 `lifespan` 事件处理器

3. **TestConnectionRequest**: 类名与测试类命名冲突
   - 需要重命名以避免 pytest 收集警告

---

## 下一步改进 (Next Steps)

1. **提高覆盖率**
   - cli.py (0%): 添加 CLI 测试
   - outputs/obsidian.py (24%): 添加 Obsidian 输出测试
   - processors/: 添加处理器逻辑测试

2. **减少警告**
   - 迁移到 Pydantic ConfigDict
   - 迁移到 FastAPI lifespan
   - 重命名冲突的类

3. **添加更多集成测试**
   - 端到端工作流测试
   - 并发请求测试
   - 性能测试

---

**最后更新**: 2026-03-10
