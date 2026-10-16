FROM python:3.12-alpine
WORKDIR /app

# Install dependencies, then remove pip: it bundles libraries with known CVEs and isn't needed at runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip uninstall -y pip setuptools wheel

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Run as a non-root user
RUN adduser -D appuser
USER appuser

EXPOSE 8000
# Migrate, then start the API. DATABASE_URL comes from docker-compose.yml.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
