FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy
CMD ["python", "hw9.py"]