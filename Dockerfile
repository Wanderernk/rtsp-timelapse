# Dockerfile.multi-stage
FROM python:3.13.2-alpine

RUN apk update && apk add ffmpeg && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# # Stage 2: Production
# FROM python:3.13.2-alpine

# # Set the working directory# Check the Dockerfile for any potential issues
# WORKDIR /app

# # Copy only the necessary files from the build stage
# COPY --from=builder /app /app

CMD ["python", "main.py"]
