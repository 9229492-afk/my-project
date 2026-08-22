"""Приветствие и справка: команды /start и /help."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

# Router — набор обработчиков одного смыслового блока.
# Подключается к Dispatcher в bot/__main__.py.
router = Router(name="start")

HELP_TEXT = "Вот что я умею:\n\n/catalog — показать товары\n/help — эта справка"


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    """Первое, что видит пользователь: /start шлётся при открытии бота."""
    # /start — это всегда «начать сначала», поэтому бросаем незаконченный заказ.
    await state.clear()

    name = message.from_user.full_name if message.from_user else "друг"

    await message.answer(
        f"Привет, {name}! 👋\n\n"
        f"Это бот магазина — здесь можно посмотреть товары и оформить заказ.\n\n"
        f"{HELP_TEXT}"
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(Command("id"))
async def handle_id(message: Message) -> None:
    """Показать Telegram ID — нужен, чтобы заполнить ADMIN_ID в .env."""
    if message.from_user is None:
        return

    await message.answer(
        f"Твой Telegram ID: <code>{message.from_user.id}</code>\n\n"
        "Впиши его в файл .env в строку ADMIN_ID — тогда заказы будут "
        "приходить сюда."
    )
