FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

EXPOSE 7860

ENV APP_PORT=7860
ENV APP_ENV=production

CMD ["python", "api.py"]