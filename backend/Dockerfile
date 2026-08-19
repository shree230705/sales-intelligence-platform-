FROM python:3.11-slim

WORKDIR /app

# System deps needed for some scientific-python wheels on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# In development, docker-compose overrides this command to use the Flask
# reloader (see docker-compose.yml). In production this is the real
# entrypoint: gunicorn talking to the app factory.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:create_app()"]
