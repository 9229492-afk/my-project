"""Тесты команды /id — она сверяет свой ID с настроенным ADMIN_ID."""

import asyncio

from bot.config import Config
from bot.handlers.start import handle_id

МОЙ_ID = 5258722824


class ЗаписьОтвета:
    """Подставное сообщение: запоминает, что бот ответил."""

    def __init__(self, user_id: int | None = МОЙ_ID) -> None:
        self.from_user = _Пользователь(user_id) if user_id is not None else None
        self.ответ: str | None = None

    async def answer(self, text: str, **kwargs: object) -> None:
        self.ответ = text


class _Пользователь:
    def __init__(self, id: int) -> None:
        self.id = id


def test_id_совпадает_с_настройкой():
    message = ЗаписьОтвета()
    asyncio.run(handle_id(message, Config(bot_token="x", admin_id=МОЙ_ID)))

    assert "✅ Совпадают" in message.ответ
    assert str(МОЙ_ID) in message.ответ


def test_id_не_совпадает_говорит_об_этом_прямо():
    """Именно этот случай ломал доставку заказов и был не виден."""
    message = ЗаписьОтвета()
    asyncio.run(handle_id(message, Config(bot_token="x", admin_id=525872282)))

    assert "❌ НЕ совпадают" in message.ответ
    assert "525872282" in message.ответ  # что настроено сейчас
    assert str(МОЙ_ID) in message.ответ  # на что менять


def test_admin_id_не_задан():
    message = ЗаписьОтвета()
    asyncio.run(handle_id(message, Config(bot_token="x", admin_id=None)))

    assert "не задан" in message.ответ
    assert str(МОЙ_ID) in message.ответ


def test_без_отправителя_не_падает():
    """Апдейт может прийти без пользователя — например, из канала."""
    message = ЗаписьОтвета(user_id=None)
    asyncio.run(handle_id(message, Config(bot_token="x", admin_id=МОЙ_ID)))

    assert message.ответ is None
