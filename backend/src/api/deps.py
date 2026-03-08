# -*- coding: utf-8 -*-
"""
鉴权依赖注入 — Multi-Tenant Ready

所有受保护的 Router 必须穿过此依赖，以实现用户身份提取。
MVP 阶段 (AUTH_ENABLED=False) 强制返回 user_id='local_admin'。
"""

import os
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


def get_auth_enabled() -> bool:
    """读取环境变量开关"""
    return os.environ.get("AUTH_ENABLED", "false").lower() in ("true", "1", "yes")


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    鉴权中间件 — 提取当前用户 ID

    - AUTH_ENABLED=False (MVP 默认):  直接返回 'local_admin'
    - AUTH_ENABLED=True  (SaaS 未来): 校验 JWT Token 并返回实际 user_id

    Returns:
        user_id: str
    """
    if not get_auth_enabled():
        # MVP 阶段：免登录，默认用户
        return "local_admin"

    # SaaS 阶段：JWT 校验（未来实现）
    if credentials is None:
        raise HTTPException(status_code=401, detail="未提供认证凭据")

    token = credentials.credentials
    # TODO: 实际 JWT 解码逻辑
    # decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    # return decoded["user_id"]

    # 临时：有 Token 就放行，返回默认用户
    return "local_admin"
