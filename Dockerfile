# Dockerfile.multi-stage
FROM python:3.13-alpine as builder

RUN apt update && apt add ffmpeg -y && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Production
FROM python:3.13-alpine

# Set the working directory# Check the Dockerfile for any potential issues
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=builder /app /app

CMD ["python", "main.py"]
