import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# 旧的 X 路由（已改为 APIRouter）
from x_legacy import router as x_router
from x_legacy import startup_db, shutdown_db

# 新的 MissAV 路由
from missav_routes import router as missav_router

# ============================================================
# 主应用
# ============================================================
app = FastAPI(title="万能媒体下载器")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 注册数据库启动/关闭事件
# ============================================================
app.add_event_handler("startup", startup_db)
app.add_event_handler("shutdown", shutdown_db)

# ============================================================
# 注册路由（都在根路径下，不覆盖）
# ============================================================

# X 旧功能：/api/search、/api/media 等路径不变
app.include_router(x_router)

# MissAV 新功能：/missav/search、/missav/info
app.include_router(missav_router)

# ============================================================
# 静态页面（两个 HTML 独立）
# ============================================================

@app.get("/")
async def root():
    """X 下载器首页"""
    return FileResponse("static/index.html")

@app.get("/missav")
async def missav_page():
    """MissAV 下载器首页"""
    return FileResponse("static/missav.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
