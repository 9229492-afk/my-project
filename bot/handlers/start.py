"""Приветствие и справка: команды /start и /help."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

# Router — набор обработчиков одного смыслового блока.
# Подключается к Dispatcher в bot/__main__.py.
router = Router(name="start")

HELP_TEXT = "Вот что я умею:\n\n/catalog — показать товары\n/help — эта справка"


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Первое, что видит пользователь: /start шлётся при открытии бота."""
    name = message.from_user.full_name if message.from_user else "друг"

    await message.answer(
        f"Привет, {name}! 👋\n\n"
        f"Это бот магазина — здесь можно посмотреть товары и оформить заказ.\n\n"
        f"{HELP_TEXT}"
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(HELP_TEXT)
