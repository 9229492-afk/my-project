"""Настройки бота: читаются из файла .env, чтобы токен не попал в git."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Настройки приложения. frozen=True — менять их после запуска нельзя."""

    bot_token: str
    # Telegram ID владельца магазина: сюда бот присылает заказы.
    # None — если ADMIN_ID ещё не заполнен: бот запустится, чтобы можно
    # было узнать свой ID командой /id, но заказы будут падать только в лог.
    admin_id: int | None


def load_config() -> Config:
    """Прочитать .env и вернуть настройки.

    Падает с понятной ошибкой, если токен не задан, — это лучше, чем
    невнятная ошибка авторизации при первом же запросе к Telegram.
    """
    load_dotenv()

    # strip() — при копировании в конец строки часто попадает пробел
    # или перенос. Сам по себе он безобиден, но aiogram отвергает такой
    # токен с невнятным «Token is invalid! It can't contains spaces».
    token = os.getenv("BOT_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "Не найден BOT_TOKEN.\n"
            "Скопируй .env.example в .env (cp .env.example .env) "
            "и вставь токен, который выдал @BotFather."
        )

    if any(char.isspace() for char in token):
        raise RuntimeError(
            "В BOT_TOKEN попал пробел или перенос строки.\n"
            "Токен — это одна сплошная строка вида 123456789:AAH...\n"
            "Скорее всего при вставке скопировалось лишнее. Впиши токен заново."
        )

    raw_admin_id = os.getenv("ADMIN_ID", "").strip()

    if not raw_admin_id:
        # Намеренно не падаем: иначе не запустить бота, чтобы узнать свой ID.
        return Config(bot_token=token, admin_id=None)

    if not raw_admin_id.isdigit():
        raise RuntimeError(
            f"ADMIN_ID должен быть числом, а сейчас там: {raw_admin_id!r}\n"
            "Нужен числовой Telegram ID, а не @username. Узнать свой — команда /id."
        )

    return Config(bot_token=token, admin_id=int(raw_admin_id))
