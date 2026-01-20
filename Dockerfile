FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
# --no-cache-dir keeps the image small by not storing pip cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src ./src

# Expose application port
EXPOSE 8001

# Run FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]