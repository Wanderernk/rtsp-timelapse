# Dockerfile.multi-stage
FROM python:3.13.2-alpine

RUN apk update && apk add ffmpeg && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
