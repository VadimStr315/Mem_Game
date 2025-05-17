FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

# Копируем весь код приложения
COPY ./app ./app

COPY .env ./app/ 

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

RUN pip install --upgrade setuptools
