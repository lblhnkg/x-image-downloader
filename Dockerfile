FROM python:3.12-slim

WORKDIR /app

# 复制依赖文件并安装 Python 包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装系统依赖（wget、ca-certificates）
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 下载并安装 sing-box v1.11.4（和你手机版本一致）
RUN wget https://github.com/SagerNet/sing-box/releases/download/v1.11.4/sing-box_1.11.4_linux_amd64.deb && \
    dpkg -i sing-box_1.11.4_linux_amd64.deb && \
    rm sing-box_1.11.4_linux_amd64.deb

# 复制整个项目
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
