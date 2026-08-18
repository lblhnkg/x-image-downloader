# ============================================================
# shared.py - 公共模块（数据库 + 工具函数）
# 所有模块共用，改一处全局生效
# ============================================================

import re
import os
import json
import asyncio
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, quote

from databases import Database
from fastapi import HTTPException

# ============================================================
# 配置
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "fushengruomeng")

if not DATABASE_URL:
    print("⚠️ 警告：DATABASE_URL 未设置，使用本地 SQLite（重启会丢数据）")
    DATABASE_URL = "sqlite:///media.db"

database = Database(DATABASE_URL)

# ============================================================
# 数据库初始化（含迁移）
# ============================================================

async def init_db():
    is_postgres = DATABASE_URL.startswith("postgresql")
    
    # 创建 media 表
    if is_postgres:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)
        await database.execute("CREATE INDEX IF NOT EXISTS idx_source ON media(data)")
    else:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)
        await database.execute("CREATE INDEX IF NOT EXISTS idx_source ON media(data)")
    
    # 创建 favorites 表
    if is_postgres:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                username TEXT PRIMARY KEY,
                name TEXT,
                addedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            await database.execute("ALTER TABLE favorites ADD COLUMN IF NOT EXISTS addedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except Exception:
            pass
    else:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                username TEXT PRIMARY KEY,
                name TEXT,
                addedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            await database.execute("ALTER TABLE favorites ADD COLUMN addedAt DATETIME DEFAULT CURRENT_TIMESTAMP")
        except Exception:
            pass

# ============================================================
# 媒体库操作
# ============================================================

async def load_all_media():
    rows = await database.fetch_all("SELECT id, data FROM media")
    library = {}
    for row in rows:
        try:
            if hasattr(row, "_mapping"):
                library[row._mapping["id"]] = json.loads(row._mapping["data"])
            else:
                library[row[0]] = json.loads(row[1])
        except:
            pass
    return library

async def save_media_item(media_id, data):
    try:
        serialized = json.dumps(data, ensure_ascii=False)
    except Exception as e:
        print(f"[DB ERROR] 序列化失败 {media_id}: {e}")
        return False, f"序列化失败: {e}"

    is_postgres = DATABASE_URL.startswith("postgresql")
    
    for attempt in range(3):
        try:
            if is_postgres:
                await database.execute(
                    """
                    INSERT INTO media (id, data)
                    VALUES (:id, :data)
                    ON CONFLICT (id) DO UPDATE
                    SET data = EXCLUDED.data
                    """,
                    {"id": media_id, "data": serialized}
                )
            else:
                await database.execute(
                    "REPLACE INTO media (id, data) VALUES (:id, :data)",
                    {"id": media_id, "data": serialized}
                )
            return True, None
        except Exception as e:
            print(f"[DB ERROR] 写入失败 (尝试 {attempt+1}/3) {media_id}: {e}")
            if attempt == 2:
                return False, str(e)
            await asyncio.sleep(0.5)
    return False, "未知错误"

async def delete_media_items(media_ids):
    if not media_ids:
        return 0
    deleted = 0
    batch_size = 100
    for i in range(0, len(media_ids), batch_size):
        batch = media_ids[i:i+batch_size]
        if DATABASE_URL.startswith("postgresql"):
            placeholders = ','.join([f'${j+1}' for j in range(len(batch))])
            query = f"DELETE FROM media WHERE id IN ({placeholders})"
            result = await database.execute(query, batch)
        else:
            placeholders = ','.join(['?'] * len(batch))
            query = f"DELETE FROM media WHERE id IN ({placeholders})"
            result = await database.execute(query, batch)
        deleted += result
    return deleted

async def clear_all_media():
    await database.execute("DELETE FROM media")

# ============================================================
# 收藏操作
# ============================================================

async def load_all_favorites():
    rows = await database.fetch_all("SELECT username, name, addedAt FROM favorites ORDER BY addedAt DESC")
    favorites = []
    for row in rows:
        if hasattr(row, "_mapping"):
            favorites.append({
                "username": row._mapping["username"],
                "name": row._mapping["name"],
                "addedAt": row._mapping.get("addedAt", datetime.now(timezone.utc).isoformat())
            })
        else:
            try:
                addedAt = row[2]
            except IndexError:
                addedAt = datetime.now(timezone.utc).isoformat()
            favorites.append({
                "username": row[0],
                "name": row[1],
                "addedAt": addedAt
            })
    return favorites

async def save_favorite(username, name):
    is_postgres = DATABASE_URL.startswith("postgresql")
    if is_postgres:
        await database.execute(
            """
            INSERT INTO favorites (username, name, addedAt)
            VALUES (:username, :name, CURRENT_TIMESTAMP)
            ON CONFLICT (username) DO UPDATE
            SET name = EXCLUDED.name, addedAt = CURRENT_TIMESTAMP
            """,
            {"username": username, "name": name}
        )
    else:
        await database.execute(
            "REPLACE INTO favorites (username, name, addedAt) VALUES (:username, :name, CURRENT_TIMESTAMP)",
            {"username": username, "name": name}
        )

async def delete_favorite(username):
    await database.execute("DELETE FROM favorites WHERE username = :username", {"username": username})

async def is_favorite(username):
    row = await database.fetch_one("SELECT 1 FROM favorites WHERE username = :username", {"username": username})
    return row is not None

# ============================================================
# 内存缓存
# ============================================================

media_library = {}

# ============================================================
# 公共工具函数
# ============================================================

def safe_filename(value):
    value = str(value or "")
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    return value[:150]

def parse_x_date(value):
    if not value:
        return None
    formats = ["%a %b %d %H:%M:%S %z %Y", "%a %b %d %H:%M:%S %Y"]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return None

def date_from_string(value, end_of_day=False):
    if not value:
        return None
    try:
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if end_of_day:
            dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        return dt
    except Exception:
        raise ValueError(f"日期格式错误：{value}")

def normalize_x_media_url(url):
    if not url:
        return ""
    url = str(url).strip()
    if not url:
        return ""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in {"pbs.twimg.com", "pbs.twimg.com.", "video.twimg.com", "video.twimg.com."}:
        return url
    query = parse_qs(parsed.query)
    if query:
        return url
    path = (parsed.path or "").lower()
    if "/media/" in path:
        return url + "?format=jpg&name=orig"
    return url

def make_proxy_url(media_url):
    if not media_url:
        return ""
    media_url = normalize_x_media_url(media_url)
    return "/api/media-proxy?url=" + quote(media_url, safe="")

def resolve_proxy_url(url):
    if not url:
        return url
    parsed = urlparse(url)
    if parsed.path != "/api/media-proxy":
        return url
    query = parse_qs(parsed.query, keep_blank_values=True)
    values = query.get("url")
    if not values:
        return url
    real_url = values[0]
    real_url = normalize_x_media_url(real_url)
    return real_url

def validate_media_url(url):
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="媒体地址格式错误")
    if parsed.scheme != "https":
        raise HTTPException(status_code=400, detail="媒体地址必须使用 HTTPS")
    hostname = (parsed.hostname or "").lower()
    allowed_hosts = {"pbs.twimg.com", "pbs.twimg.com.", "video.twimg.com", "video.twimg.com."}
    if hostname not in allowed_hosts:
        raise HTTPException(status_code=400, detail="不是有效的 X 媒体地址")
    return url

def validate_hls_url(url):
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="视频地址格式错误")
    if parsed.scheme != "https":
        raise HTTPException(status_code=400, detail="视频地址必须使用 HTTPS")
    hostname = (parsed.hostname or "").lower()
    allowed_hosts = {
        "video.twimg.com", "video.twimg.com.",
        "missav.com", "missav.ws", "cdn.missav.com",
    }
    if hostname not in allowed_hosts:
        pass
    return url

# ============================================================
# MissAV / Jable 独立数据库连接（追加）
# ============================================================
MISSAV_DATABASE_URL = os.environ.get("MISSAV_DATABASE_URL")
if MISSAV_DATABASE_URL:
    missav_db = Database(MISSAV_DATABASE_URL)
else:
    missav_db = None
    print("⚠️ 警告：MISSAV_DATABASE_URL 未设置，MissAV/Jable 功能将不可用")
