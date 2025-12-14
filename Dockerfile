# Используем базовый образ с Python
FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости, чтобы Docker кэшировал слой
COPY requirements.txt .

# Ставим зависимости
# --no-cache-dir уменьшает размер образа
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта в контейнер
COPY . .

# Указываем команду для запуска бота
CMD ["python", "-m", "app.bot.main"]
