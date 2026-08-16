# ============================================================
# app.py - 主入口（只负责挂载路由和静态页）
# ============================================================

import os
import requests
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

# ============================================================
# 预热函数
# ============================================================
def warm_up_proxy():
    """在应用启动时预热 sing-box 的 urltest，确保节点选择已完成"""
    proxy_url = "http://127.0.0.1:1081"
    try:
        print("[预热] 正在通过代理预热 urltest...")
        resp = requests.get(
            "https://www.google.com",
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=10
        )
        if resp.status_code == 200:
            print("[预热] urltest 预热成功，节点已选择")
        else:
            print(f"[预热] 预热返回状态码 {resp.status_code}，但继续启动")
    except Exception as e:
        print(f"[预热] 预热失败（不影响启动）: {e}")

# ============================================================
# 启动/关闭事件
# ============================================================
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

    # 预热 sing-box 的 urltest（非阻塞，但会等待最多 10 秒）
    warm_up_proxy()

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
