"""Кнопки каталога.

Кнопки под сообщением (inline-кнопки) при нажатии не пишут текст в чат,
а присылают боту callback — небольшую строку данных. Чтобы не собирать
эти строки руками, aiogram даёт CallbackData: класс описывает, какие
поля лежат внутри, и сам занимается упаковкой и разбором.
"""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.catalog import Product, format_price


class ProductCallback(CallbackData, prefix="product"):
    """Нажали на товар в списке."""

    product_id: str


class CatalogCallback(CallbackData, prefix="catalog"):
    """Нажали кнопку самого каталога (например, «назад»)."""

    action: str


def catalog_keyboard(products: tuple[Product, ...]) -> InlineKeyboardMarkup:
    """Список товаров: по кнопке на каждый товар."""
    builder = InlineKeyboardBuilder()

    for product in products:
        builder.button(
            text=f"{product.name} — {format_price(product.price)}",
            callback_data=ProductCallback(product_id=product.id),
        )

    builder.adjust(1)  # по одной кнопке в ряд, иначе названия обрежутся
    return builder.as_markup()


def product_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата из карточки товара в список."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Назад в каталог",
        callback_data=CatalogCallback(action="back"),
    )
    return builder.as_markup()
