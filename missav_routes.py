# ============================================================
# missav_routes.py - MissAV 采集存储模块（新版）
# 功能：接收油猴脚本回传的数据，提供采集列表查询
# 数据库：使用 MISSAV_DATABASE_URL（独立数据库）
# ============================================================

import os
from fastapi import APIRouter, Request, HTTPException
from databases import Database
from pydantic import BaseModel

# ============================================================
# 数据库连接
# ============================================================

MISSAV_DATABASE_URL = os.environ.get("MISSAV_DATABASE_URL")
if not MISSAV_DATABASE_URL:
    raise RuntimeError("❌ MISSAV_DATABASE_URL 环境变量未设置")

missav_db = Database(MISSAV_DATABASE_URL)

# ============================================================
# 路由定义
# ============================================================

router = APIRouter(prefix="/api/missav", tags=["MissAV"])


# ============================================================
# 数据模型
# ============================================================

class CollectItem(BaseModel):
    video_id: str          # MissAV 影片编号，如 "ssis-001"
    title: str             # 影片标题
    publish_date: str | None = None   # 发布日期（如果页面有）
    cover_url: str | None = None      # 封面图片地址
    m3u8_url: str          # m3u8 视频流地址


# ============================================================
# API 接口
# ============================================================

@router.post("/collect")
async def collect_missav_item(request: Request, item: CollectItem):
    """
    油猴脚本采集数据回传接口
    
    开发者模式（有 Session Cookie）→ 存入 MISSAV_DATABASE_URL
    访客模式（无 Session Cookie）→ 不存数据库，直接返回成功（由前端存 localStorage）
    """
    # 检查是否登录（开发者模式）
    session_cookie = request.cookies.get("session")
    
    if not session_cookie:
        # 访客模式：不存数据库，直接返回成功
        return {
            "ok": True,
            "stored": False,
            "message": "访客模式，请前端自行存入 localStorage"
        }
    
    # ===== 开发者模式：写入数据库 =====
    try:
        # 检查是否已存在（去重，如果存在则更新）
        existing = await missav_db.fetch_one(
            "SELECT id FROM missav_items WHERE video_id = :video_id",
            {"video_id": item.video_id}
        )
        
        if existing:
            # 已存在 → 更新（m3u8 地址可能变化，封面/标题也可能更新）
            await missav_db.execute(
                """
                UPDATE missav_items
                SET title = :title,
                    publish_date = :publish_date,
                    cover_url = :cover_url,
                    m3u8_url = :m3u8_url,
                    created_at = CURRENT_TIMESTAMP
                WHERE video_id = :video_id
                """,
                {
                    "video_id": item.video_id,
                    "title": item.title,
                    "publish_date": item.publish_date,
                    "cover_url": item.cover_url,
                    "m3u8_url": item.m3u8_url,
                }
            )
        else:
            # 不存在 → 插入新记录
            await missav_db.execute(
                """
                INSERT INTO missav_items (video_id, title, publish_date, cover_url, m3u8_url)
                VALUES (:video_id, :title, :publish_date, :cover_url, :m3u8_url)
                """,
                {
                    "video_id": item.video_id,
                    "title": item.title,
                    "publish_date": item.publish_date,
                    "cover_url": item.cover_url,
                    "m3u8_url": item.m3u8_url,
                }
            )
        
        return {
            "ok": True,
            "stored": True,
            "message": "已存入云端数据库"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {str(e)}")


@router.get("/my-items")
async def get_missav_items(request: Request):
    """
    获取我的 MissAV 采集列表
    
    开发者模式 → 返回数据库全部记录（因为只有你一个人用）
    访客模式 → 返回空列表（前端从 localStorage 读取）
    """
    session_cookie = request.cookies.get("session")
    
    if not session_cookie:
        # 访客模式：返回空列表
        return {
            "ok": True,
            "items": [],
            "mode": "guest"
        }
    
    # ===== 开发者模式：查询全部记录 =====
    try:
        rows = await missav_db.fetch_all(
            """
            SELECT id, video_id, title, publish_date, cover_url, m3u8_url, created_at
            FROM missav_items
            ORDER BY created_at DESC
            """
        )
        
        items = []
        for row in rows:
            items.append({
                "id": row["id"],
                "video_id": row["video_id"],
                "title": row["title"],
                "publish_date": row["publish_date"],
                "cover_url": row["cover_url"],
                "m3u8_url": row["m3u8_url"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            })
        
        return {
            "ok": True,
            "items": items,
            "mode": "developer"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
