# Використовуємо офіційний образ Python
FROM python:3.11-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл залежностей
COPY requirements.txt .

# Встановлюємо залежності
# Оновлюємо pip та встановлюємо залежності без кешу
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту в робочу директорію
COPY . .

# Збираємо статичні файли (згідно з налаштуваннями WhiteNoise)
# STATIC_ROOT у settings.py вказує на 'staticfiles'
RUN python manage.py collectstatic --noinput

# Відкриваємо порт, на якому працюватиме Gunicorn
EXPOSE 8000

# Запускаємо застосунок за допомогою Gunicorn
# Переконайтеся, що gunicorn є у вашому requirements.txt (він є)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "vaysedshop.wsgi:application"]