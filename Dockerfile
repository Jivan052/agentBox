FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from the environment package
COPY AgentBox/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project sources
COPY AgentBox /app/AgentBox

# Ensure imports like "from src.env import ..." resolve correctly
ENV PYTHONPATH=/app/AgentBox

EXPOSE 7860

CMD ["uvicorn", "src.env:app", "--host", "0.0.0.0", "--port", "7860"]