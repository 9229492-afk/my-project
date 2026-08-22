"""Настройки бота: читаются из файла .env, чтобы токен не попал в git."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Настройки приложения. frozen=True — менять их после запуска нельзя."""

    bot_token: str
    admin_id: int  # твой Telegram ID: сюда бот присылает заказы


def load_config() -> Config:
    """Прочитать .env и вернуть настройки.

    Падает с понятной ошибкой, если токен не задан, — это лучше, чем
    невнятная ошибка авторизации при первом же запросе к Telegram.
    """
    load_dotenv()

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден BOT_TOKEN.\n"
            "Скопируй .env.example в .env (cp .env.example .env) "
            "и вставь токен, который выдал @BotFather."
        )

    admin_id = os.getenv("ADMIN_ID")
    if not admin_id:
        raise RuntimeError(
            "Не найден ADMIN_ID.\n"
            "Это твой Telegram ID — узнать его можно, отправив боту команду /id."
        )

    if not admin_id.isdigit():
        raise RuntimeError(f"ADMIN_ID должен быть числом, а сейчас там: {admin_id!r}")

    return Config(bot_token=token, admin_id=int(admin_id))
