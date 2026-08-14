# ============================================================
# bilibili_routes.py - Bilibili 下载器（占位模块）
# ============================================================

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(prefix="/bilibili", tags=["Bilibili"])

@router.get("/")
async def bilibili_home():
    return {"message": "Bilibili 下载器开发中，敬请期待"}

@router.get("/search")
async def bilibili_search(keyword: str = Query(..., min_length=1)):
    # TODO: 实现 B站搜索
    return {"ok": False, "detail": "功能开发中"}

@router.get("/info")
async def bilibili_info(bvid: str = Query(...)):
    # TODO: 获取视频信息
    return {"ok": False, "detail": "功能开发中"}
