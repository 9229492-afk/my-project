# Образ для хостинга: сервис соберёт его сам и будет держать бота запущенным.
FROM python:3.11-slim

WORKDIR /app

# Зависимости ставим отдельным слоем: пока requirements.txt не менялся,
# при пересборке этот шаг берётся из кэша и деплой идёт быстрее.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot/

# Не root — если внутрь контейнера кто-то пролезет, прав у него будет меньше.
RUN useradd --create-home appuser
USER appuser

# BOT_TOKEN и ADMIN_ID сюда не кладём: их задают в настройках хостинга,
# иначе токен окажется внутри образа.
CMD ["python", "-m", "bot"]
