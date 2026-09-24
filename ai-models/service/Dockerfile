FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing pyc files to disc & buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ai-models source files, models, and service code
COPY src/ ./src/
COPY models/ ./models/
COPY service/ ./service/

EXPOSE 8001

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8001"]
