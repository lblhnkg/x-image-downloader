FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV SING_BOX_VERSION=1.13.18
RUN wget https://github.com/SagerNet/sing-box/releases/download/v${SING_BOX_VERSION}/sing-box-${SING_BOX_VERSION}-linux-amd64.tar.gz && \
    tar -xzf sing-box-${SING_BOX_VERSION}-linux-amd64.tar.gz && \
    mv sing-box-${SING_BOX_VERSION}-linux-amd64/sing-box /usr/local/bin/ && \
    chmod +x /usr/local/bin/sing-box && \
    rm -rf sing-box-${SING_BOX_VERSION}-linux-amd64.tar.gz sing-box-${SING_BOX_VERSION}-linux-amd64

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "sing-box run -c config.json & sleep 3 && uvicorn app:app --host 0.0.0.0 --port 8000"]
