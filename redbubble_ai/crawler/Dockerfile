FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright && playwright install --with-deps

COPY . .

CMD ["python", "main.py"] 