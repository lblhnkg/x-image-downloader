# ============================================================
# missav_routes.py - MissAV 下载器（基于 missAV_api 官方库）
# 功能：番号查找 / 播放（HLS 直链代理）/ 下载（HLS→MP4）
# 维护者：EchterAlsFake/missAV_api（PyPI: missAV_api）
# 适配：lblhnkg/x-image-downloader v5.0test
#
# ⚠️ 许可证：missAV_api 为 AGPL-3.0
#    本项目为个人使用、非商用、全开源，符合 AGPL 要求
# ============================================================

import os
import re
import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse

# missAV_api 官方库（pip install "missAV_api[full]"）
from missav_api import Client, DownloadConfigHLS

router = APIRouter(prefix="/missav", tags=["MissAV"])

# ============================================================
# 配置（全部从环境变量读取，不写死任何敏感信息）
# ============================================================

# 可选：自定义请求延迟（秒），避免被限速
REQUEST_DELAY = float(os.environ.get("MISSAV_DELAY", "0.5"))

# 可选：HTTP 代理（如 "http://user:pass@host:port"）
PROXY = os.environ.get("MISSAV_PROXY", "")

# 可选：下载文件存放目录
DOWNLOAD_DIR = os.environ.get("MISSAV_DOWNLOAD_DIR", "/tmp/missav_downloads")
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

# 单例 Client（复用连接、复用缓存）
_client = None

def get_client():
    """获取（或创建）全局异步 Client"""
    global _client
    if _client is None:
        kwargs = {"request_delay": REQUEST_DELAY}
        if PROXY:
            kwargs["proxy"] = PROXY
        _client = Client(**kwargs)
        print(f"[MissAV] Client 初始化（delay={REQUEST_DELAY}s, proxy={'有' if PROXY else '无'}）")
    return _client

# ============================================================
# 工具函数
# ============================================================

def _normalize_code(raw: str) -> str:
    """规范化番号：去空格、大写、保留连字符，兼容 'SSIS 001'"""
    if not raw:
        return ""
    s = raw.strip().upper().replace(" ", "-")
    m = re.match(r"^([A-Z]{2,6})\s*[-\s]?\s*(\d{3,5})$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return s

def _resolve_video_id(video_id: str) -> str:
    """把用户输入的番号/URL 统一成完整 missav.ai URL"""
    vid = (video_id or "").strip()
    if not vid:
        raise HTTPException(status_code=400, detail="番号或视频地址不能为空")
    if vid.startswith("http"):
        return vid
    return f"https://missav.ai/{_normalize_code(vid)}"

def _build_item_from_video(video) -> dict:
    """把 missAV_api 的 Video 对象转成前端需要的 dict"""
    return {
        "id": getattr(video, "video_code", "") or "",
        "code": getattr(video, "video_code", "") or "",
        "title": getattr(video, "title", "") or "未知标题",
        "url": getattr(video, "url", "") or "",
        "cover": getattr(video, "thumbnail", "") or "",
        "video_url": getattr(video, "m3u8_base_url", "") or "",
        "actors": list(getattr(video, "etiquette", []) or []),
        "genres": list(getattr(video, "genres", []) or []),
        "series": getattr(video, "series", "") or "",
        "manufacturer": getattr(video, "manufacturer", "") or "",
        "publish_date": getattr(video, "publish_date", "") or "",
        "description": "",
    }

def _safe_filename(value: str) -> str:
    """清理文件名，去掉非法字符"""
    value = str(value or "")
    value = re.sub(r'[\/:*?"|]+', "_", value)
    return value[:100] or "missav"

# ============================================================
# 1) 搜索接口 —— 番号 / 关键词 / 演员名 都能搜
#    前端调用：GET /missav/search?q=SSIS-001
# ============================================================
@router.get("/search")
async def missav_search(
    q: str = Query(..., min_length=1, description="番号 / 关键词 / 演员名"),
    limit: int = Query(30, ge=1, le=100, description="最多返回条数"),
):
    client = get_client()
    keyword = _normalize_code(q)

    results = []
    seen_codes = set()
    try:
        count = 0
        async for video in client.search(query=keyword, video_count=limit):
            item = _build_item_from_video(video)
            # 去重（同一番号可能出现在不同语言路径下）
            key = item["code"] or item["url"]
            if key in seen_codes:
                continue
            seen_codes.add(key)

            # 搜索结果里 m3u8 可能为空，补抓详情
            if not item["video_url"] and item.get("url"):
                try:
                    detail = await client.get_video(item["url"])
                    item["video_url"] = getattr(detail, "m3u8_base_url", "") or ""
                    if not item["actors"]:
                        item["actors"] = list(getattr(detail, "etiquette", []) or [])
                except Exception:
                    pass

            results.append(item)
            count += 1
            if count >= limit:
                break
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {e}")
    return {"ok": True, "count": len(results), "items": results}

# ============================================================
# 2) 详情接口 —— 给前端 modal 播放用
#    前端调用：GET /missav/info?video_id=SSIS-001
# ============================================================
@router.get("/info")
async def missav_info(
    video_id: str = Query(..., description="番号（如 SSIS-001）或完整视频 URL"),
):
    client = get_client()
    url = _resolve_video_id(video_id)
    try:
        video = await client.get_video(url)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到该影片: {e}")

    item = _build_item_from_video(video)
    item["url"] = url
    return {"ok": True, "item": item}

# ============================================================
# 3) 播放接口（代理 m3u8，绕开 CORS / Referer 校验）
#    前端调用：GET /missav/stream?video_id=SSIS-001&quality=1080p
#    也兼容旧路径 /api/video-stream?url=...
# ============================================================
@router.get("/stream")
async def missav_stream(
    video_id: str = Query(..., description="番号或视频 URL"),
    quality: str = Query("best", description="best / 1080p / 720p / worst"),
):
    client = get_client()
    url = _resolve_video_id(video_id)

    try:
        video = await client.get_video(url)
        m3u8_url = getattr(video, "m3u8_base_url", "") or ""
        if not m3u8_url:
            raise HTTPException(status_code=404, detail="该影片无可播放的 m3u8 流")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取流失败: {e}")

    # 用正确 headers 拉取 m3u8（Referer + Origin 是 surrit.com 防盗链必需的）
    headers = {
        "Referer": "https://missav.ai/",
        "Origin": "https://missav.ai",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    try:
        # 优先用 client 内部的 session（自带指纹伪装）
        session = getattr(client, "_session", None)
        if session is not None:
            resp = await asyncio.to_thread(session.get, m3u8_url, headers=headers, timeout=30)
            content = resp.text
        else:
            import requests
            resp = requests.get(m3u8_url, headers=headers, timeout=30)
            resp.raise_for_status()
            content = resp.text
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"拉取 m3u8 失败: {e}")

    # 把 m3u8 里的相对分片 URL 改写成绝对 URL（播放器才能正确加载 .ts）
    base = m3u8_url.rsplit("/", 1)[0] + "/"
    rewritten = []
    for line in content.splitlines():
        if line and not line.startswith("#") and not line.startswith("http"):
            line = base + line
        rewritten.append(line)
    content = "\n".join(rewritten) + "\n"

    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="application/vnd.apple.mpegurl",
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
        },
    )

# ============================================================
# 4) 下载接口 —— HLS 下载并合并成 MP4
#    前端调用：GET /missav/download?video_id=SSIS-001&quality=best
#    也兼容旧路径 /api/video-download?url=...&filename=...
# ============================================================
@router.get("/download")
async def missav_download(
    video_id: str = Query(..., description="番号或视频 URL"),
    quality: str = Query("best", description="best / 1080p / 720p / worst"),
):
    client = get_client()
    url = _resolve_video_id(video_id)

    try:
        video = await client.get_video(url)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到该影片: {e}")

    code = getattr(video, "video_code", "") or "missav"
    safe_name = _safe_filename(code)
    out_path = Path(DOWNLOAD_DIR) / f"{safe_name}.mp4"

    # 已下载过就直接返回（断点续传留给库内部处理）
    if out_path.exists() and out_path.stat().st_size > 0:
        return FileResponse(path=out_path, media_type="video/mp4", filename=f"{safe_name}.mp4")

    try:
        await video.download(
            DownloadConfigHLS(
                quality=quality,
                path=str(out_path),
                remux=True,  # TS → MP4 合并
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {e}")

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise HTTPException(status_code=500, detail="下载完成但未找到文件")

    return FileResponse(path=out_path, media_type="video/mp4", filename=f"{safe_name}.mp4")

# ============================================================
# 5) 兼容旧路径 —— 前端 missav.html 里写死了这两个 URL
#    /api/video-stream?url=...       → 内部转发到 /missav/stream
#    /api/video-download?url=...&filename=... → 内部转发到 /missav/download
# ============================================================
# 注意：兼容端点 /api/video-stream 和 /api/video-download
# 已统一在 app.py 里实现，避免和本路由前缀冲突。

# ============================================================
# 健康检查
# ============================================================
@router.get("/health")
async def missav_health():
    return {
        "status": "ok",
        "module": "missav",
        "library": "missAV_api",
        "download_dir": DOWNLOAD_DIR,
    }
