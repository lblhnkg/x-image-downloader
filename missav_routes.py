# ============================================================
# missav_routes.py - MissAV 下载器（使用 unofficial-api-for-missav）
# 完全自动处理 Cloudflare 5秒盾，无需用户手动设置 Cookie
# ============================================================

import os
import re
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from missav_api import Client
import asyncio

router = APIRouter(prefix="/missav", tags=["MissAV"])

# ============================================================
# 配置
# ============================================================
# 如果你有代理，可以在这里设置（可选）
# PROXY = os.environ.get("MISSAV_PROXY")  # 例如 http://user:pass@host:port
PROXY = None  # 默认不使用代理

# 全局客户端实例（可复用）
client = None

def get_client():
    """获取或创建 MissAV 客户端（单例）"""
    global client
    if client is None:
        # 如果配置了代理，传入 proxy 参数
        if PROXY:
            client = Client(proxy=PROXY)
        else:
            client = Client()
        print("[MissAV] 客户端初始化成功（自动处理 Cloudflare）")
    return client

# ============================================================
# API 模型（保留兼容，但不再使用）
# ============================================================
class CookieSet(BaseModel):
    cookie_string: str

# 保留这些接口但不做实际存储，返回成功（兼容前端）
@router.post("/set-cookie")
async def set_cookie(data: CookieSet):
    """兼容接口：新版本已自动处理，无需手动设置"""
    return {"ok": True, "message": "自动模式已启用，无需手动设置 Cookie"}

@router.get("/cookie-status")
async def cookie_status():
    """始终返回已设置状态"""
    return {"ok": True, "has_cookie": True, "message": "自动抓取已启用"}

# ============================================================
# MissAV 搜索和详情（使用库 API）
# ============================================================
@router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        client = get_client()
        # 调用库的搜索方法（异步）
        items = await client.search(q)
        # 格式化返回结果（与之前的 API 保持一致）
        formatted = []
        for item in items:
            formatted.append({
                "id": item.get("id") or "",
                "url": item.get("url") or "",
                "title": item.get("title") or "",
                "code": item.get("code") or "",
                "cover": item.get("cover") or "",
                # 其他字段可选
            })
        return {"ok": True, "count": len(formatted), "items": formatted}
    except Exception as e:
        print(f"[MissAV] 搜索失败: {e}")
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        client = get_client()
        # 调用库的详情方法（异步）
        detail = await client.detail(video_id)
        # 格式化返回
        result = {
            "id": detail.get("id") or video_id,
            "code": detail.get("code") or "",
            "title": detail.get("title") or "",
            "cover": detail.get("cover") or "",
            "actors": detail.get("actors") or [],
            "description": detail.get("description") or "",
            "video_url": detail.get("video_url") or "",
            "url": detail.get("url") or "",
        }
        return {"ok": True, "item": result}
    except Exception as e:
        print(f"[MissAV] 详情获取失败: {e}")
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")
