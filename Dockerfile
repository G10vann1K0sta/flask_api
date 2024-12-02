FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["flask", "db", "upgrade"] && ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:create_app()"]