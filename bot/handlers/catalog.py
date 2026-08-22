"""Каталог товаров: команда /catalog и нажатия на кнопки."""

from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

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

    await _replace_message(
        callback,
        text=format_product(product),
        reply_markup=product_keyboard(product.id),
        photo=product.photo,
    )

    # Telegram ждёт ответа на каждое нажатие. Без этой строки у пользователя
    # будет крутиться часик на кнопке, пока не отвалится по таймауту.
    await callback.answer()


@router.callback_query(CatalogCallback.filter(F.action == "back"))
async def back_to_catalog(callback: CallbackQuery) -> None:
    """Нажали «назад» — вернуть список товаров."""
    await _replace_message(
        callback,
        text=CATALOG_TITLE,
        reply_markup=catalog_keyboard(all_products()),
    )

    await callback.answer()


async def _replace_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup,
    photo: str | None = None,
) -> None:
    """Заменить сообщение: удалить старое и отправить новое.

    Через edit_text нельзя превратить сообщение с фотографией в текстовое
    и наоборот — Telegram этого не разрешает. Поэтому заменяем целиком,
    а не редактируем: так одинаково работает и для товаров с фото, и без.
    """
    message = callback.message

    if not isinstance(message, Message):
        return  # сообщение слишком старое, Telegram его уже не отдаёт

    # Удаление может не пройти: сообщения старше двух суток удалять нельзя.
    # Это не повод ломать показ товара — просто оставим старое в чате.
    with suppress(TelegramAPIError):
        await message.delete()

    if photo:
        await message.answer_photo(photo, caption=text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)
