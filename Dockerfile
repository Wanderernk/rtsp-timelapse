# Dockerfile.multi-stage
FROM python:3.13-slim

COPY --from=mwader/static-ffmpeg:7.1 /ffmpeg /usr/local/bin/
# RUN apk update && apk --no-cache add ffmpeg && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
