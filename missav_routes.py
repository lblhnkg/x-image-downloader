# ============================================================
# missav_routes.py - MissAV 模块（V2 + 数据库诊断）
# ============================================================

import os

from databases import Database
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from pydantic import BaseModel


# ============================================================
# 数据库
# ============================================================

MISSAV_DATABASE_URL = os.environ.get("MISSAV_DATABASE_URL")

if not MISSAV_DATABASE_URL:
    raise RuntimeError(
        "❌ MISSAV_DATABASE_URL 环境变量未设置"
    )

missav_db = Database(MISSAV_DATABASE_URL)


# ============================================================
# 数据库表
# ============================================================

MISSAV_TABLE = "public.missav_items"


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/api/missav",
    tags=["MissAV"]
)


# ============================================================
# Model
# ============================================================

class CollectItem(BaseModel):

    video_id: str

    title: str

    actress: str | None = None

    description: str | None = None

    publish_date: str | None = None

    cover_url: str | None = None

    m3u8_url: str

    source_url: str | None = None


# ============================================================
# 工具
# ============================================================

def is_developer(request: Request):

    return bool(
        request.cookies.get("session")
    )


# ============================================================
# 数据库诊断
# ============================================================

@router.get("/debug-db")
async def debug_db():

    try:

        identity = await missav_db.fetch_one(
            """
            SELECT
                current_database() AS database_name,
                current_user AS user_name,
                current_schema() AS schema_name,
                inet_server_addr() AS server_address,
                inet_server_port() AS server_port,
                current_setting('search_path') AS search_path
            """
        )

        table_info = await missav_db.fetch_one(
            """
            SELECT
                table_catalog,
                table_schema,
                table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'missav_items'
            """
        )

        table_count = None

        if table_info:

            table_count = await missav_db.fetch_val(
                f"""
                SELECT COUNT(*)
                FROM {MISSAV_TABLE}
                """
            )

        return {

            "ok": True,

            "connection": {

                "database": identity["database_name"]
                if identity
                else None,

                "user": identity["user_name"]
                if identity
                else None,

                "schema": identity["schema_name"]
                if identity
                else None,

                "server_address": str(
                    identity["server_address"]
                )
                if identity and identity["server_address"]
                else None,

                "server_port": identity["server_port"]
                if identity
                else None,

                "search_path": identity["search_path"]
                if identity
                else None
            },

            "missav_items": {

                "exists": bool(table_info),

                "catalog": (
                    table_info["table_catalog"]
                    if table_info
                    else None
                ),

                "schema": (
                    table_info["table_schema"]
                    if table_info
                    else None
                ),

                "table": (
                    table_info["table_name"]
                    if table_info
                    else None
                ),

                "count": table_count
            }
        }

    except Exception as e:

        return {

            "ok": False,

            "error": str(e)
        }


# ============================================================
# 采集
# ============================================================

@router.post("/collect")
async def collect_missav_item(
    request: Request,
    item: CollectItem
):

    if not is_developer(request):

        return {
            "ok": True,
            "stored": False,
            "message": "guest mode"
        }

    try:

        existing = await missav_db.fetch_one(
            f"""
            SELECT id
            FROM {MISSAV_TABLE}
            WHERE video_id=:video_id
            """,
            {
                "video_id": item.video_id
            }
        )

        params = {

            "video_id": item.video_id,

            "title": item.title,

            "actress": item.actress,

            "description": item.description,

            "publish_date": item.publish_date,

            "cover_url": item.cover_url,

            "m3u8_url": item.m3u8_url,

            "source_url": item.source_url
        }

        if existing:

            await missav_db.execute(
                f"""
                UPDATE {MISSAV_TABLE}

                SET

                    title=:title,

                    actress=:actress,

                    description=:description,

                    publish_date=:publish_date,

                    cover_url=:cover_url,

                    m3u8_url=:m3u8_url,

                    source_url=:source_url,

                    created_at=CURRENT_TIMESTAMP

                WHERE video_id=:video_id
                """,
                params
            )

        else:

            await missav_db.execute(
                f"""
                INSERT INTO {MISSAV_TABLE}(
                    
                    video_id,

                    title,

                    actress,

                    description,

                    publish_date,

                    cover_url,

                    m3u8_url,

                    source_url

                )

                VALUES(

                    :video_id,

                    :title,

                    :actress,

                    :description,

                    :publish_date,

                    :cover_url,

                    :m3u8_url,

                    :source_url

                )
                """,
                params
            )

        return {
            "ok": True,
            "stored": True
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# 获取全部
# ============================================================

@router.get("/my-items")
async def get_items(
    request: Request
):

    if not is_developer(request):

        return {
            "ok": True,
            "items": [],
            "mode": "guest"
        }

    try:

        rows = await missav_db.fetch_all(
            f"""
            SELECT *

            FROM {MISSAV_TABLE}

            ORDER BY created_at DESC
            """
        )

        items = []

        for row in rows:

            items.append({

                "id": row["id"],

                "video_id": row["video_id"],

                "title": row["title"],

                "actress": row["actress"],

                "description": row["description"],

                "publish_date": row["publish_date"],

                "cover_url": row["cover_url"],

                "m3u8_url": row["m3u8_url"],

                "source_url": row["source_url"],

                "created_at": (
                    row["created_at"].isoformat()
                    if row["created_at"]
                    else None
                )
            })

        return {

            "ok": True,

            "items": items,

            "mode": "developer"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# 搜索
# ============================================================

@router.get("/search")
async def search_items(
    q: str = ""
):

    try:

        rows = await missav_db.fetch_all(
            f"""
            SELECT *

            FROM {MISSAV_TABLE}

            WHERE

                LOWER(video_id)
                LIKE LOWER(:q)

                OR

                LOWER(title)
                LIKE LOWER(:q)

            ORDER BY created_at DESC
            """,
            {
                "q": f"%{q}%"
            }
        )

        return {

            "ok": True,

            "items": [dict(row) for row in rows]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# 女优搜索
# ============================================================

@router.get("/actress/{name}")
async def actress_items(
    name: str
):

    try:

        rows = await missav_db.fetch_all(
            f"""
            SELECT *

            FROM {MISSAV_TABLE}

            WHERE

                LOWER(actress)
                LIKE LOWER(:name)

            ORDER BY created_at DESC
            """,
            {
                "name": f"%{name}%"
            }
        )

        return {

            "ok": True,

            "items": [dict(row) for row in rows]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# 统计
# ============================================================

@router.get("/stats")
async def stats():

    try:

        total = await missav_db.fetch_val(
            f"""
            SELECT COUNT(*)

            FROM {MISSAV_TABLE}
            """
        )

        actresses = await missav_db.fetch_val(
            f"""
            SELECT COUNT(
                DISTINCT actress
            )

            FROM {MISSAV_TABLE}
            """
        )

        return {

            "ok": True,

            "total": total,

            "actresses": actresses
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# 清空
# ============================================================

@router.delete("/clear")
async def clear_items(
    request: Request
):

    if not is_developer(request):

        raise HTTPException(
            status_code=403,
            detail="permission denied"
        )

    try:

        await missav_db.execute(
            f"""
            DELETE FROM {MISSAV_TABLE}
            """
        )

        return {

            "ok": True
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# 预留：同步我的喜欢
# ============================================================

@router.post("/sync-saved")
async def sync_saved():

    return {

        "ok": False,

        "message": "not implemented"
    }
