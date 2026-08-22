"""Оформление заказа: пошаговый диалог и отправка заказа владельцу магазина."""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from bot.catalog import find_product
from bot.config import Config
from bot.keyboards.order import (
    BuyCallback,
    ConfirmCallback,
    confirm_keyboard,
    phone_request_keyboard,
)
from bot.orders import (
    Order,
    clean_address,
    clean_name,
    format_order_for_admin,
    format_order_summary,
    normalize_phone,
)
from bot.states import OrderStates

logger = logging.getLogger(__name__)

router = Router(name="order")


@router.message(Command("cancel"))
async def cancel_order(message: Message, state: FSMContext) -> None:
    """Прервать оформление на любом шаге."""
    if await state.get_state() is None:
        await message.answer("Сейчас нечего отменять. /catalog — посмотреть товары")
        return

    await state.clear()
    await message.answer(
        "Заказ отменён. /catalog — посмотреть товары",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.callback_query(BuyCallback.filter())
async def start_order(
    callback: CallbackQuery, callback_data: BuyCallback, state: FSMContext
) -> None:
    """Нажали «Купить» — начинаем диалог."""
    product = find_product(callback_data.product_id)

    if product is None:
        await callback.answer("Такого товара больше нет", show_alert=True)
        return

    # Запоминаем товар и переходим на первый шаг.
    await state.set_state(OrderStates.name)
    await state.update_data(product_id=product.id)

    if isinstance(callback.message, Message):
        await callback.message.answer(
            f"Оформляем заказ: <b>{product.name}</b>\n\n"
            "Как тебя зовут?\n\n"
            "Передумал — отправь /cancel"
        )

    await callback.answer()


@router.message(OrderStates.name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = clean_name(message.text or "")

    if name is None:
        await message.answer("Не похоже на имя. Напиши, как к тебе обращаться:")
        return

    await state.update_data(customer_name=name)
    await state.set_state(OrderStates.phone)
    await message.answer(
        f"Приятно познакомиться, {name}!\n\n"
        "Теперь номер телефона — напиши его или нажми кнопку ниже:",
        reply_markup=phone_request_keyboard(),
    )


@router.message(OrderStates.phone, F.contact)
async def process_phone_from_contact(message: Message, state: FSMContext) -> None:
    """Покупатель нажал кнопку — Telegram прислал номер сам."""
    contact = message.contact
    phone = normalize_phone(contact.phone_number) if contact else None

    if phone is None:
        await message.answer("Не смог разобрать номер. Напиши его текстом:")
        return

    await _ask_address(message, state, phone)


@router.message(OrderStates.phone)
async def process_phone_from_text(message: Message, state: FSMContext) -> None:
    phone = normalize_phone(message.text or "")

    if phone is None:
        await message.answer("Не похоже на номер телефона. Пример: +7 999 123-45-67")
        return

    await _ask_address(message, state, phone)


async def _ask_address(message: Message, state: FSMContext, phone: str) -> None:
    """Общий шаг после телефона — чтобы не дублировать код в двух обработчиках."""
    await state.update_data(phone=phone)
    await state.set_state(OrderStates.address)
    await message.answer(
        "Куда доставить? Напиши адрес:",
        reply_markup=ReplyKeyboardRemove(),  # убираем кнопку с телефоном
    )


@router.message(OrderStates.address)
async def process_address(message: Message, state: FSMContext) -> None:
    address = clean_address(message.text or "")

    if address is None:
        await message.answer("Адрес слишком короткий. Напиши город, улицу и дом:")
        return

    await state.update_data(address=address)

    order = await _build_order(state)
    if order is None:
        await state.clear()
        await message.answer("Что-то пошло не так, начни заново: /catalog")
        return

    await state.set_state(OrderStates.confirm)
    await message.answer(format_order_summary(order), reply_markup=confirm_keyboard())


@router.callback_query(OrderStates.confirm, ConfirmCallback.filter(F.action == "no"))
async def reject_order(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    if isinstance(callback.message, Message):
        await callback.message.edit_text("Заказ отменён. /catalog — посмотреть товары")

    await callback.answer()


@router.callback_query(OrderStates.confirm, ConfirmCallback.filter(F.action == "yes"))
async def accept_order(
    callback: CallbackQuery, state: FSMContext, bot: Bot, config: Config
) -> None:
    """Подтвердили заказ — отправляем его владельцу магазина в личку."""
    order = await _build_order(state)
    await state.clear()

    if order is None or callback.from_user is None:
        await callback.answer("Что-то пошло не так, начни заново", show_alert=True)
        return

    text = format_order_for_admin(
        order, user_id=callback.from_user.id, username=callback.from_user.username
    )

    try:
        await bot.send_message(config.admin_id, text)
    except TelegramAPIError:
        # Заказ не должен потеряться: пишем его в лог целиком.
        logger.exception("Не удалось отправить заказ админу. Заказ: %s", order)

        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                "Заказ принят, но уведомить магазин не получилось. "
                "Свяжись с нами напрямую, пожалуйста."
            )
        await callback.answer()
        return

    logger.info("Заказ оформлен: %s", order)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "✅ Заказ принят! Мы свяжемся с тобой по указанному телефону.\n\n"
            "/catalog — посмотреть остальные товары"
        )

    await callback.answer()


async def _build_order(state: FSMContext) -> Order | None:
    """Собрать заказ из того, что накопилось в FSM. None — если данных не хватает."""
    data = await state.get_data()

    product = find_product(data.get("product_id", ""))
    name = data.get("customer_name")
    phone = data.get("phone")
    address = data.get("address")

    if product is None or not name or not phone or not address:
        return None

    return Order(product=product, customer_name=name, phone=phone, address=address)
