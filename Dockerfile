# 使用官方 Python 轻量镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（FFmpeg + sing-box 下载工具）
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 下载并安装 sing-box v1.10.0（最新稳定版）
ENV SING_BOX_VERSION=1.10.0
RUN wget https://github.com/SagerNet/sing-box/releases/download/v${SING_BOX_VERSION}/sing-box-${SING_BOX_VERSION}-linux-amd64.zip && \
    unzip -q sing-box-${SING_BOX_VERSION}-linux-amd64.zip && \
    mv sing-box-${SING_BOX_VERSION}-linux-amd64/sing-box /usr/local/bin/ && \
    chmod +x /usr/local/bin/sing-box && \
    rm -rf sing-box-${SING_BOX_VERSION}-linux-amd64.zip sing-box-${SING_BOX_VERSION}-linux-amd64

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令：先起 sing-box，再起 uvicorn
CMD ["sh", "-c", "sing-box run -c config.json & sleep 3 && uvicorn app:app --host 0.0.0.0 --port 8000"]
