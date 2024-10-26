FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .


# Install dependencies in a virtual environment
RUN python -m venv venv &&\
./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV REDIS_URL=redis://redis:6379

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
