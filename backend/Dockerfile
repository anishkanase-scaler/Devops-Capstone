FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 appuser

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Run as a normal user, not root
USER 10001
EXPOSE 8000

# Run all migrations first, then start the API. DATABASE_URL comes from docker-compose.yml.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
