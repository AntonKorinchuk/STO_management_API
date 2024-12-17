FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "sleep 45 && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
