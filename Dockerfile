# Use official lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered streaming
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8080

# Set working directory to /app
WORKDIR /app

# Copy dependency definition and install packages
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application package into /app/backend
COPY backend/ backend/

# Expose default Cloud Run port
EXPOSE 8080

# Run Uvicorn server dynamically binding to the runtime PORT
CMD exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}
