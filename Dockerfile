FROM python:3.13-slim

RUN apt-get update && apt-get install ffmpeg -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]