FROM python:3.11-slim

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Application code
COPY src ./src

# Create runtime data directory and fix permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8001

EXPOSE 8001

# Drop privileges
USER appuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]