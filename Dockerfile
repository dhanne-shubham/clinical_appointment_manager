# ============================
# 1. Use official Python image
# ============================
FROM python:3.10-slim

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1

# ============================
# 2. Set work directory
# ============================
WORKDIR /app

# ============================
# 3. Install system dependencies
# ============================
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ============================
# 4. Copy requirements
# ============================
COPY requirements.txt /app/

# ============================
# 5. Install Python dependencies
# ============================
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# 6. Copy Django project
# ============================
COPY . /app/

# ============================
# 7. Expose port
# ============================
EXPOSE 8000

# ============================
# 8. Run Django server
# ============================
CMD ["bash", "-c", "\
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py create_default_superuser && \
    python manage.py runserver 0.0.0.0:8000 \
"]