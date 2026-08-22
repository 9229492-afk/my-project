"""Каталог товаров: команда /catalog и нажатия на кнопки."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.catalog import all_products, find_product, format_product
from bot.keyboards.catalog import (
    CatalogCallback,
    ProductCallback,
    catalog_keyboard,
    product_keyboard,
)

router = Router(name="catalog")

CATALOG_TITLE = "Выбери товар:"


@router.message(Command("catalog"))
async def show_catalog(message: Message) -> None:
    """Показать список товаров."""
    await message.answer(CATALOG_TITLE, reply_markup=catalog_keyboard(all_products()))


@router.callback_query(ProductCallback.filter())
async def show_product(callback: CallbackQuery, callback_data: ProductCallback) -> None:
    """Нажали на товар — показать его карточку вместо списка."""
    product = find_product(callback_data.product_id)

    if product is None:
        # Товар мог исчезнуть из каталога, пока сообщение висело в чате.
        await callback.answer("Такого товара больше нет", show_alert=True)
        return

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            format_product(product),
            reply_markup=product_keyboard(product.id),
        )

    # Telegram ждёт ответа на каждое нажатие. Без этой строки у пользователя
    # будет крутиться часик на кнопке, пока не отвалится по таймауту.
    await callback.answer()


@router.callback_query(CatalogCallback.filter(F.action == "back"))
async def back_to_catalog(callback: CallbackQuery) -> None:
    """Нажали «назад» — вернуть список товаров."""
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            CATALOG_TITLE,
            reply_markup=catalog_keyboard(all_products()),
        )

    await callback.answer()
