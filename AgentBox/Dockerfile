FROM python:3.11-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
	build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY openenv.yaml .
COPY inference.py .

# Expose port
EXPOSE 7860

# Run FastAPI app
CMD ["uvicorn", "src.env:app", "--host", "0.0.0.0", "--port", "7860"]
