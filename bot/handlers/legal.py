"""Публичная оферта и правила возврата: команды /oferta и /vozvrat.

Файлы лежат прямо в bot/legal/ и отправляются с диска — хостить их
отдельно не нужно. Именно это обычно и просит платёжный агрегатор
(например, ЮKassa) при подключении приёма платежей: оферта и правила
возврата должны быть видны покупателю прямо в месте покупки, то есть
в этом боте.
"""

from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

router = Router(name="legal")

# bot/handlers/legal.py -> bot/handlers -> bot -> bot/legal
LEGAL_DIR = Path(__file__).resolve().parent.parent / "legal"

OFERTA_PATH = LEGAL_DIR / "oferta.pdf"
VOZVRAT_PATH = LEGAL_DIR / "vozvrat.pdf"


@router.message(Command("oferta"))
async def handle_oferta(message: Message) -> None:
    """Прислать публичную оферту (условия покупки в этом боте)."""
    await message.answer_document(
        FSInputFile(OFERTA_PATH),
        caption="📄 Публичная оферта ООО «ФЕНИКС» — условия покупки в этом боте.",
    )


@router.message(Command("vozvrat"))
async def handle_vozvrat(message: Message) -> None:
    """Прислать правила возврата и обмена товара."""
    await message.answer_document(
        FSInputFile(VOZVRAT_PATH),
        caption="📄 Правила возврата и обмена товара ООО «ФЕНИКС».",
    )
