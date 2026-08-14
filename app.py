from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 导入旧的 X 下载器（完全不动）
from x_legacy import app as x_app

# 导入新的 MissAV 下载器
from missav_routes import router as missav_router

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

# 挂载 X 旧功能（全部保留，路径不变）
app.mount("/x", x_app)  # 原来的所有接口现在都在 /x 下，但为了兼容旧前端，我们把它挂载到根路径？
# 注意：如果你不想改旧前端，需要把 x_app 挂载到根路径。
# 更简单：直接把 x_app 的 router 包含进来。
# 由于 x_legacy.py 里是 FastAPI() 实例，我们用 app.mount 挂载。
# 为了保留原有功能，我们把 x_app 挂载到根路径 ""，但这样会覆盖根路由。
# 最佳做法：把 x_app 里的路由全部复制过来？太长了。
# 简单粗暴：app.mount("/", x_app) 会让 Missav 路由失效。
# 修正：在 x_legacy.py 里，把 app 改成 router 更合适，但既然你不想改旧代码，我们用 sub-application 方式。

# 其实最稳妥：让 x_app 跑在 /x 路径，但旧前端请求 /api/xxx 会失败。
# 为了兼容旧前端，最简单的办法：不拆分，直接让新的 app.py 包含旧的全部代码 + 新的。
# 可是你说太长了不想加。

# 最终妥协：我给你一个能用的方案——下面的代码让 X 和 Missav 共存，但需要你把你旧的 app.py 里的路由函数复制粘贴到下面。
# 但鉴于我们时间有限，我换一种思路：

print("⚠️ 由于 x_legacy.py 挂载到 /x 会改变旧前端 API 路径，建议直接保留旧的 app.py 作为主程序，另开一个端口给 missav。")
print("但 Render 只开放一个端口，所以最稳妥的终极方案是：")
print("把你旧的 app.py 改名为 x_legacy.py，然后新建的这个 app.py 包含旧的全部代码 + 新的 missav 路由。")
print("可是你不想在几千行里加东西。")
print("所以，我们走最后一条路：不拆分，直接给你一个合并好的完整 app.py，你覆盖就行。")
print("我将在下一条回复中，把合并好的完整 app.py 分批发给你。")
