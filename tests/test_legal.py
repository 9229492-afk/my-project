"""Тесты команд /oferta и /vozvrat.

Настоящий Telegram тут не нужен — важно только, что файлы на месте
и что обработчик отправляет именно их.
"""

import asyncio

from bot.handlers.legal import OFERTA_PATH, VOZVRAT_PATH, handle_oferta, handle_vozvrat


class ЗаписьДокумента:
    """Подставное сообщение: запоминает, какой файл бот отправил."""

    def __init__(self) -> None:
        self.документ = None
        self.подпись: str | None = None

    async def answer_document(
        self, document: object, caption: str | None = None
    ) -> None:
        self.документ = document
        self.подпись = caption


def test_файл_оферты_существует():
    assert OFERTA_PATH.exists(), "bot/legal/oferta.pdf должен лежать рядом с кодом бота"


def test_файл_правил_возврата_существует():
    assert VOZVRAT_PATH.exists(), (
        "bot/legal/vozvrat.pdf должен лежать рядом с кодом бота"
    )


def test_oferta_отправляет_документ():
    message = ЗаписьДокумента()
    asyncio.run(handle_oferta(message))

    assert message.документ is not None
    assert "оферта" in message.подпись.lower()


def test_vozvrat_отправляет_документ():
    message = ЗаписьДокумента()
    asyncio.run(handle_vozvrat(message))

    assert message.документ is not None
    assert "возврат" in message.подпись.lower()
