# ============================================================
# app.py - 主入口（只负责挂载路由和静态页）
# ============================================================

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from shared import database, init_db, missav_db

# 导入各模块路由
from x_routes import router as x_router
from jable_routes import router as jable_router
from bilibili_routes import router as bilibili_router

# 创建主应用
app = FastAPI(title="万能媒体下载器")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库事件
@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()
    if missav_db is not None:
        await missav_db.connect()
        print("[MissAV DB] 连接成功")
    else:
        print("[MissAV DB] 未配置，跳过")
    print("[DB] 主数据库连接成功")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    if missav_db is not None:
        await missav_db.disconnect()
        print("[MissAV DB] 已断开")
    print("[DB] 主数据库已断开")

# ============================================================
# 注册路由
# ============================================================

app.include_router(x_router)          # X API（/api/*）
app.include_router(jable_router)      # Jable API（/api/jable/*）
app.include_router(bilibili_router)   # Bilibili API（/bilibili/*）

# ============================================================
# 静态页面
# ============================================================

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/x")
async def x_page():
    return FileResponse("static/x.html")

@app.get("/missav")
async def missav_page():
    return FileResponse("static/missav.html")

@app.get("/bilibili")
async def bilibili_page():
    return FileResponse("static/bilibili.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
