"""Кнопки оформления заказа."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class BuyCallback(CallbackData, prefix="buy"):
    """Нажали «Купить» в карточке товара."""

    product_id: str


class ConfirmCallback(CallbackData, prefix="confirm"):
    """Подтверждение заказа: action — 'yes' или 'no'."""

    action: str


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=ConfirmCallback(action="yes"))
    builder.button(text="❌ Отменить", callback_data=ConfirmCallback(action="no"))
    builder.adjust(2)
    return builder.as_markup()


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка «поделиться телефоном».

    Это обычная кнопка под полем ввода (не inline). По ней Telegram сам
    отправит номер, привязанный к аккаунту, — покупателю не надо его печатать.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="📱 Отправить мой номер", request_contact=True)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
