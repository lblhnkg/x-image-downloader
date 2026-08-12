import os
import re
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

from xtf import Router

app = FastAPI(title="X Image Finder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_username(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("请输入 X 博主主页")

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    parsed = urlparse(value)
    host = parsed.netloc.lower()

    if host not in {
        "x.com",
        "www.x.com",
        "twitter.com",
        "www.twitter.com",
    }:
        raise ValueError(
            "请输入类似 https://x.com/username 的主页链接"
        )

    parts = [p for p in parsed.path.split("/") if p]

    if not parts:
        raise ValueError("没有识别到 X 用户名")

    username = parts[0]

    if username.lower() in {
        "home",
        "explore",
        "search",
        "i",
        "notifications",
        "messages",
    }:
        raise ValueError("这不是博主主页链接")

    username = re.sub(r"[^A-Za-z0-9_]", "", username)

    if not username:
        raise ValueError("用户名无效")

    return username


def obj_to_dict(obj):
    if isinstance(obj, dict):
        return obj

    if hasattr(obj, "to_dict"):
        return obj.to_dict()

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if hasattr(obj, "__dict__"):
        return obj.__dict__

    return {}


def extract_media(tweet):
    data = obj_to_dict(tweet)

    media = (
        data.get("media")
        or data.get("media_urls")
        or data.get("mediaURLs")
        or []
    )

    result = []

    if isinstance(media, dict):
        possible = []

        for key in (
            "all",
            "photos",
            "images",
            "media",
        ):
            value = media.get(key)
            if value:
                if isinstance(value, list):
                    possible.extend(value)
                else:
                    possible.append(value)

        media = possible

    if isinstance(media, str):
        media = [media]

    for item in media or []:

        if isinstance(item, str):
            url = item

            if "pbs.twimg.com" in url:
                result.append({
                    "url": url,
                    "thumb": url,
                })

            continue

        if not isinstance(item, dict):
            continue

        url = (
            item.get("url")
            or item.get("media_url")
            or item.get("media_url_https")
            or item.get("original_url")
            or item.get("original")
        )

        thumb = (
            item.get("thumbnail_url")
            or item.get("thumbnail")
            or url
        )

        if url:
            result.append({
                "url": url,
                "thumb": thumb,
                "width": item.get("width"),
                "height": item.get("height"),
            })

    return result


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "message": "X Image Finder is running"
    }


@app.get("/api/timeline")
def timeline(
    profile: str = Query(...),
    limit: int = Query(100, ge=1, le=200),
):
    try:
        username = get_username(profile)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    try:
        # 使用当前 x-tweet-fetcher v3 的标准 Python API。
        # 不强制指定 backend，让 Router 使用它自己的 backend 路由。
        router = Router()

        tweets = router.fetch_timeline(
            username,
            limit=limit
        )

    except Exception as e:

        # 不再把上游失败伪装成“0 张图片”。
        raise HTTPException(
            status_code=502,
            detail=(
                "X 时间线获取失败。"
                f"后端返回：{str(e)}"
            )
        )

    items = []

    for tweet in tweets:

        data = obj_to_dict(tweet)

        tweet_id = (
            data.get("tweet_id")
            or data.get("id")
            or ""
        )

        tweet_url = (
            data.get("url")
            or data.get("tweet_url")
        )

        if not tweet_url and tweet_id:
            tweet_url = (
                f"https://x.com/"
                f"{username}/status/{tweet_id}"
            )

        created_at = (
            data.get("created_at")
            or data.get("date")
            or data.get("time_ago")
            or ""
        )

        text = (
            data.get("text")
            or data.get("full_text")
            or ""
        )

        media = extract_media(tweet)

        for index, photo in enumerate(media):

            image_url = photo.get("url")

            if not image_url:
                continue

            items.append({
                "id": f"{tweet_id}-{index}",
                "tweet_id": tweet_id,
                "tweet_url": tweet_url,
                "created_at": created_at,
                "text": text,
                "image": image_url,
                "thumb": photo.get("thumb") or image_url,
                "width": photo.get("width"),
                "height": photo.get("height"),
            })

    return {
        "username": username,
        "count": len(items),
        "items": items,
    }


@app.get("/api/download")
async def download(
    url: str = Query(...)
):

    parsed = urlparse(url)

    allowed_hosts = {
        "pbs.twimg.com",
        "video.twimg.com",
    }

    if (
        parsed.scheme != "https"
        or parsed.netloc.lower() not in allowed_hosts
    ):
        raise HTTPException(
            status_code=400,
            detail="只允许下载 X 官方媒体地址"
        )

    # 如果 URL 没有 format/orig 参数，
    # 对常见 pbs.twimg.com 图片尝试请求原始尺寸。
    if "pbs.twimg.com" in parsed.netloc:
        if "format=" not in url:
            separator = "&" if "?" in url else "?"
            url += separator + "format=jpg&name=orig"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15"
        )
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30,
            headers=headers,
        ) as client:

            response = await client.get(url)

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"读取 X 原图失败：{e}"
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=(
                "X 原图读取失败。"
                "请点击“打开原帖”从 X 保存。"
            )
        )

    content_type = response.headers.get(
        "content-type",
        "image/jpeg"
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
        }
    )
