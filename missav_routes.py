# ============================================================
# missav_routes.py - MissAV 下载器（使用 unofficial-api-for-missav）
# 支持指纹切换和代理，完全自动处理 Cloudflare
# ============================================================

import os
from fastapi import APIRouter, HTTPException, Query
from missav_api import Client

router = APIRouter(prefix="/missav", tags=["MissAV"])

# ============================================================
# 配置（从环境变量读取）
# ============================================================
PROXY = os.environ.get("MISSAV_PROXY")  # 例如 http://user:pass@host:port
IMPERSONATION = os.environ.get("MISSAV_IMPERSONATION", "chrome124")  # 默认 chrome124

# 全局客户端单例
_client = None

def get_client():
    global _client
    if _client is None:
        kwargs = {"impersonation": IMPERSONATION}
        if PROXY:
            kwargs["proxy"] = PROXY
        _client = Client(**kwargs)
        print(f"[MissAV] 客户端初始化成功（指纹: {IMPERSONATION}）")
    return _client

# ============================================================
# API 接口（保持不变）
# ============================================================
@router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        client = get_client()
        items = []
        async for item in client.search(q):
            items.append(item)
            if len(items) >= 30:
                break
        formatted = []
        for item in items:
            formatted.append({
                "id": item.get("id") or "",
                "url": item.get("url") or "",
                "title": item.get("title") or "",
                "code": item.get("code") or "",
                "cover": item.get("cover") or "",
            })
        return {"ok": True, "count": len(formatted), "items": formatted}
    except Exception as e:
        print(f"[MissAV] 搜索失败: {e}")
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        client = get_client()
        detail = await client.detail(video_id)
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
