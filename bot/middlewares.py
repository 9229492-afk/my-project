"""Middleware — код, который выполняется до обработчика, для каждого апдейта.

Здесь он нужен ровно для одного: писать в лог, кто именно пишет боту.
Так ID владельца можно узнать прямо из терминала, не полагаясь на то,
что ответ бота дойдёт.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

logger = logging.getLogger(__name__)


class LogUserMiddleware(BaseMiddleware):
    """Пишет в лог, от кого пришёл апдейт."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # aiogram кладёт отправителя в data под ключом event_from_user.
        user = data.get("event_from_user")

        if isinstance(user, User):
            logger.info(
                "Сообщение от %s (id %s) — это и есть его Telegram ID",
                user.full_name,
                user.id,
            )

        return await handler(event, data)
