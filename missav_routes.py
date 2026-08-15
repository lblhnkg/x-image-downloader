# ============================================================
# missav_routes.py - MissAV 下载器（基于 missAV_api 2.2.1）
# 支持限速、代理、指纹配置
# ============================================================

import os
from fastapi import APIRouter, HTTPException, Query
from missav_api import Client, DownloadConfigHLS
from base_api.modules.config import config
from base_api.base import BaseCore

router = APIRouter(prefix="/missav", tags=["MissAV"])

# ============================================================
# 配置（从环境变量读取）
# ============================================================
PROXY = os.environ.get("MISSAV_PROXY")
IMPERSONATION = os.environ.get("MISSAV_IMPERSONATION", "chrome124")

# 配置限速和延迟（降低被屏蔽风险）
config.request_delay = 5  # 请求间隔 5 秒
config.bandwidth_limit = 1.0  # 限速 1MB/s

# 全局客户端单例
_client = None

def get_client():
    global _client
    if _client is None:
        core = BaseCore(config=config)
        core.configuration.impersonation = IMPERSONATION
        if PROXY:
            core.configuration.proxy = PROXY
        core.enable_logging()
        _client = Client(core=core)
        print(f"[MissAV] 客户端初始化成功（指纹: {IMPERSONATION}，限速已启用）")
    return _client

# ============================================================
# API 接口
# ============================================================
@router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        client = get_client()
        # 搜索（返回 AsyncGenerator）
        items = []
        async for item in client.search(q):
            items.append(item)
            if len(items) >= 30:
                break
        # 格式化返回
        formatted = []
        for item in items:
            formatted.append({
                "id": item.get("id") or "",
                "url": item.get("url") or "",
                "title": item.get("title") or "",
                "code": item.get("video_code") or "",  # 新版属性名
                "cover": item.get("thumbnail") or "",
            })
        return {"ok": True, "count": len(formatted), "items": formatted}
    except Exception as e:
        print(f"[MissAV] 搜索失败: {e}")
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        client = get_client()
        # 新版：使用视频 ID 或完整 URL
        video_url = f"https://missav.ws/en/{video_id}"
        video = await client.get_video(video_url)
        # 加载元数据
        await video.load_fields("title", "video_code", "publish_date", "genres", "series", "manufacturer", "thumbnail", "m3u8_base_url")
        result = {
            "id": video_id,
            "code": video.video_code or "",
            "title": video.title or "",
            "cover": video.thumbnail or "",
            "actors": video.genres or [],
            "description": f"发行日期: {video.publish_date}" if video.publish_date else "",
            "video_url": video.m3u8_base_url or "",
            "url": video_url,
        }
        return {"ok": True, "item": result}
    except Exception as e:
        print(f"[MissAV] 详情获取失败: {e}")
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")
