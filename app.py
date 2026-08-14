import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# 旧的 X 下载器（完整保留，路径不变）
from x_legacy import app as x_app

# 新的 MissAV 下载器（独立路由）
from missav_routes import router as missav_router

# ============================================================
# 主应用
# ============================================================
app = FastAPI(title="万能媒体下载器")

# CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 挂载子应用
# ============================================================

# X 功能挂载到根路径（保持旧前端完全兼容）
app.mount("/", x_app)

# MissAV 功能挂载到 /missav 路径
from fastapi import FastAPI
missav_app = FastAPI()
missav_app.include_router(missav_router)
app.mount("/missav", missav_app)

# ============================================================
# 静态页面
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
    """健康检查"""
    return {"status": "ok"}

# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
