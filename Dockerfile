# Base image with Python runtime
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire source tree into container (src will be included)
COPY . .

# Run FastAPI from src.main path
CMD ["uvicorn", "src.main.app:app", "--host", "0.0.0.0", "--port", "8000"]
