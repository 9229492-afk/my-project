"""Приветствие и справка: команды /start и /help."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import Config

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
async def handle_id(message: Message, config: Config) -> None:
    """Показать свой ID и тот, что настроен, — и сразу сказать, сходятся ли.

    Раньше команда показывала только свой ID, и сверять его с настройкой
    приходилось вручную. Из-за этого расхождение обнаруживалось лишь тогда,
    когда заказ не доходил.
    """
    if message.from_user is None:
        return

    свой = message.from_user.id
    настроен = config.admin_id

    if настроен is None:
        итог = (
            "⚠️ ADMIN_ID не задан — заказы никуда не отправляются.\n"
            f"Впиши <code>{свой}</code> в настройки и перезапусти бота."
        )
    elif настроен == свой:
        итог = "✅ Совпадают — заказы будут приходить в этот чат."
    else:
        итог = (
            "❌ НЕ совпадают — поэтому заказы и не доходят.\n"
            f"Замени ADMIN_ID на <code>{свой}</code>, "
            "а потом пересоздай окружение: секреты подхватываются только "
            "при создании."
        )

    await message.answer(
        f"Твой Telegram ID: <code>{свой}</code>\n"
        f"Сейчас в настройках ADMIN_ID: <code>{настроен}</code>\n\n"
        f"{итог}"
    )
