# Dockerfile (production)
FROM python:3.11-slim

# Install tesseract and build deps, then clean apt cache
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

# It's okay to not set ENV PORT here; Render will set PORT at runtime.
# But we keep a default for local testing.
ENV PORT=10000

# Start with gunicorn and bind to the PORT environment variable provided by Render
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --worker-class gthread --log-level info"]

