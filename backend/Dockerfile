FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

EXPOSE 8081
CMD ["sh", "-c", "python -m alembic -c backend/alembic.ini upgrade head && python backend/run.py --host 0.0.0.0 --port 8081"]
