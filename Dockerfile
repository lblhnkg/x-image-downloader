# 使用官方 Python 轻量镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（FFmpeg 用于 X 视频 HLS 转 MP4 + 下载 sing-box 所需工具）
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 下载并安装 sing-box v1.11.4（稳定版）
ENV SING_BOX_VERSION=1.11.4
RUN wget https://github.com/SagerNet/sing-box/releases/download/v${SING_BOX_VERSION}/sing-box-${SING_BOX_VERSION}-linux-amd64.zip && \
    unzip -q sing-box-${SING_BOX_VERSION}-linux-amd64.zip && \
    mv sing-box-${SING_BOX_VERSION}-linux-amd64/sing-box /usr/local/bin/ && \
    chmod +x /usr/local/bin/sing-box && \
    rm -rf sing-box-${SING_BOX_VERSION}-linux-amd64.zip sing-box-${SING_BOX_VERSION}-linux-amd64

# 复制依赖文件并安装（利用 Docker 缓存层，加快构建）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目（包括所有 .py 文件和 static 目录）
COPY . .

# 暴露端口（Render 会通过环境变量 PORT 覆盖）
EXPOSE 8000

# 启动：先运行 sing-box（后台），等待 3 秒后启动 uvicorn
CMD ["sh", "-c", "sing-box run -c config.json & sleep 3 && uvicorn app:app --host 0.0.0.0 --port 8000"]
