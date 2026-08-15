# 使用官方 Python 轻量镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装（利用 Docker 缓存层，加快构建）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目（包括所有 .py 文件和 static 目录）
COPY . .

# 暴露端口（Render 会通过环境变量 PORT 覆盖）
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
