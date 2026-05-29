FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY data /app/data

ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV PYTHONPATH=/app

WORKDIR /app/backend

CMD ["python", "app.py"]
