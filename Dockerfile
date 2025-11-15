# Dockerfile
FROM python:3.11-slim

# Install tesseract and small tooling, then clean apt cache
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      tesseract-ocr \
      libtesseract-dev \
      libleptonica-dev \
      build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

# Use the PORT Render provides
ENV PORT=10000

# Start command (use sh -c so $PORT is expanded)
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]
