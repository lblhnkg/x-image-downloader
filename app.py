import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="X Image Finder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


FX_API = "https://api.fxtwitter.com"


def get_username(profile: str) -> str:
    """从 X 主页链接提取用户名"""

    profile = profile.strip()

    if not profile:
        raise ValueError("请输入 X 博主主页链接")

    if not profile.startswith(("http://", "https://")):
        profile = "https://" + profile

    parsed = urlparse(profile)
    host = parsed.netloc.lower()

    if host not in {
        "x.com",
        "www.x.com",
        "twitter.com",
        "www.twitter.com",
    }:
        raise ValueError(
            "请输入类似 https://x.com/username 的 X 主页链接"
        )

    parts = [x for x in parsed.path.split("/") if x]

    if not parts:
        raise ValueError("无法识别 X 用户名")

    username = parts[0]

    if username.lower() in {
        "home",
        "explore",
        "search",
        "i",
        "notifications",
        "messages",
        "settings",
    }:
        raise ValueError("这不是有效的 X 博主主页")

    username = re.sub(r"[^A-Za-z0-9_]", "", username)

    if not username:
        raise ValueError("用户名无效")

    return username


def parse_x_date(value):
    """解析 FxTwitter 的 created_at"""

    if not value:
        return None

    try:
        # 例如：
        # Tue Aug 11 20:53:00 +0000 2026
        dt = datetime.strptime(
            value,
            "%a %b %d %H:%M:%S %z %Y"
        )

        return dt.astimezone(timezone.utc)

    except Exception:
        return None


def date_from_string(value, end_of_day=False):
    """解析网页传来的 YYYY-MM-DD"""

    if not value:
        return None

    try:
        dt = datetime.strptime(
            value,
            "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc)

        if end_of_day:
            dt = dt.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            )

        return dt

    except Exception:
        raise ValueError(
            f"日期格式错误：{value}"
        )


async def fetch_media_page(
    username: str,
    cursor: str | None = None,
    count: int = 100,
):
    """获取一个用户的一页媒体帖子"""

    params = {
        "count": min(count, 100)
    }

    if cursor:
        params["cursor"] = cursor

    url = (
        f"{FX_API}/2/profile/"
        f"{username}/media"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 "
            "Version/18.0 Mobile/15E148 Safari/604.1"
        )
    }

    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers=headers,
    ) as client:

        response = await client.get(
            url,
            params=params,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=(
                f"FxTwitter 返回 HTTP "
                f"{response.status_code}"
            ),
        )

    try:
        data = response.json()
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="FxTwitter 返回的不是有效 JSON",
        )

    if data.get("code") != 200:
        raise HTTPException(
            status_code=502,
            detail=(
                "FxTwitter 返回错误："
                + str(data)
            ),
        )

    return data.get("results", []), data.get(
        "cursor",
        {}
    )


def extract_photos(tweet):
    """从帖子中提取真正的照片"""

    media = tweet.get("media") or {}

    photos = media.get("photos") or []

    result = []

    for index, photo in enumerate(photos):

        if not isinstance(photo, dict):
            continue

        url = photo.get("url")

        if not url:
            continue

        result.append({
            "id": str(
                photo.get("id")
                or f"{tweet.get('id')}-{index}"
            ),
            "url": url,
            "width": photo.get("width"),
            "height": photo.get("height"),
            "alt": photo.get("altText") or "",
        })

    return result


@app.get("/")
async def index():
    return FileResponse(
        "static/index.html"
    )


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "service": "X Image Finder",
    }


@app.get("/api/search")
async def search(
    profile: str = Query(...),
    start_date: str | None = None,
    end_date: str | None = None,
    max_pages: int = Query(
        100,
        ge=1,
        le=100,
    ),
):
    """
    搜索用户图片。

    时间范围：
    start_date = YYYY-MM-DD
    end_date   = YYYY-MM-DD

    max_pages：
    最多翻多少页，每页最多 100 条。
    """

    try:
        username = get_username(profile)

        start_dt = date_from_string(
            start_date
        )

        end_dt = date_from_string(
            end_date,
            end_of_day=True
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if (
        start_dt
        and end_dt
        and start_dt > end_dt
    ):
        raise HTTPException(
            status_code=400,
            detail="开始日期不能晚于结束日期",
        )

    all_images = []

    cursor = None
    pages = 0

    # 防止某些异常情况下 cursor 一直循环
    seen_cursors = set()

    while pages < max_pages:

        pages += 1

        tweets, cursor_data = await fetch_media_page(
            username,
            cursor=cursor,
            count=100,
        )

        if not tweets:
            break

        reached_older_than_start = False

        for tweet in tweets:

            created_at_text = (
                tweet.get("created_at")
                or ""
            )

            created_at = parse_x_date(
                created_at_text
            )

            # 如果无法解析日期，跳过
            if not created_at:
                continue

            # FxTwitter 返回通常是从新到旧。
            #
            # 如果已经比开始日期更早，
            # 后面继续翻只会越来越旧，
            # 所以可以停止。
            if start_dt and created_at < start_dt:
                reached_older_than_start = True
                continue

            # 比结束日期更新
            if end_dt and created_at > end_dt:
                continue

            photos = extract_photos(tweet)

            for photo in photos:

                all_images.append({
                    "id": (
                        f"{tweet.get('id')}-"
                        f"{photo['id']}"
                    ),
                    "tweet_id": str(
                        tweet.get("id") or ""
                    ),
                    "tweet_url": (
                        tweet.get("url")
                        or (
                            f"https://x.com/"
                            f"{username}/status/"
                            f"{tweet.get('id')}"
                        )
                    ),
                    "created_at": (
                        created_at_text
                    ),
                    "timestamp": (
                        int(created_at.timestamp())
                    ),
                    "text": (
                        tweet.get("text")
                        or ""
                    ),
                    "image": photo["url"],
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                    "alt": photo.get("alt") or "",
                })

        # 如果已经进入开始日期以前，
        # 没必要继续翻历史。
        if (
            start_dt
            and reached_older_than_start
        ):
            break

        next_cursor = (
            cursor_data.get("bottom")
            if isinstance(cursor_data, dict)
            else None
        )

        if not next_cursor:
            break

        if next_cursor in seen_cursors:
            break

        seen_cursors.add(next_cursor)

        cursor = next_cursor

    # 最新 → 最旧
    all_images.sort(
        key=lambda x: x["timestamp"],
        reverse=True,
    )

    return {
        "ok": True,
        "username": username,
        "count": len(all_images),
        "pages": pages,
        "items": all_images,
    }


@app.get("/api/download")
async def download(
    url: str = Query(...)
):
    """
    下载 X 原图。

    只允许 pbs.twimg.com。
    """

    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or parsed.netloc.lower()
        not in {
            "pbs.twimg.com",
            "pbs.twimg.com.",
        }
    ):
        raise HTTPException(
            status_code=400,
            detail="不是有效的 X 图片地址",
        )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 "
            "Version/18.0 Mobile/15E148 Safari/604.1"
        )
    }

    try:

        async with httpx.AsyncClient(
            timeout=60,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = await client.get(url)

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=f"下载原图失败：{e}",
        )

    if response.status_code >= 400:

        raise HTTPException(
            status_code=response.status_code,
            detail=(
                "X 图片服务器拒绝了下载请求，"
                "请尝试打开原帖保存图片。"
            ),
        )

    content_type = response.headers.get(
        "content-type",
        "image/jpeg",
    )

    if "png" in content_type:
        filename = "x-original.png"
    elif "webp" in content_type:
        filename = "x-original.webp"
    else:
        filename = "x-original.jpg"

    return StreamingResponse(
        iter([response.content]),
        media_type=content_type,
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )
