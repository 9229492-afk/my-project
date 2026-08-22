"""Заказ: данные, проверка введённого и тексты сообщений.

Как и bot/catalog.py, этот модуль ничего не знает про Telegram — только
про то, что такое корректный телефон и как выглядит текст заказа.
Поэтому всё это проверяется тестами без запуска бота.
"""

from dataclasses import dataclass

from bot.catalog import Product, format_price


@dataclass(frozen=True)
class Order:
    """Готовый заказ на один товар."""

    product: Product
    customer_name: str
    phone: str
    address: str


def clean_name(raw: str) -> str | None:
    """Привести имя в порядок. None — если имя не годится."""
    name = " ".join(raw.split())  # убираем лишние пробелы и переносы строк

    if len(name) < 2 or len(name) > 100:
        return None

    if not any(char.isalpha() for char in name):
        return None  # "12345" или "???" — это не имя

    return name


def normalize_phone(raw: str) -> str | None:
    """Привести телефон к виду +79991234567. None — если это не телефон.

    Люди пишут телефон как угодно: '8 (999) 123-45-67', '+7 999 1234567'.
    Поэтому сначала оставляем одни цифры, а потом смотрим, что получилось.
    """
    digits = "".join(char for char in raw if char.isdigit())

    if len(digits) == 11 and digits[0] in "78":
        return "+7" + digits[1:]

    if len(digits) == 10:  # написали без кода страны
        return "+7" + digits

    return None


def clean_address(raw: str) -> str | None:
    """Привести адрес в порядок. None — если адрес слишком короткий."""
    address = " ".join(raw.split())

    if len(address) < 5 or len(address) > 300:
        return None

    return address


def format_order_for_admin(order: Order, user_id: int, username: str | None) -> str:
    """Текст заказа, который придёт владельцу магазина в личку."""
    if username:
        contact = f"@{username}"
    else:
        # Без username написать можно только по ссылке вида tg://user?id=...
        contact = f'<a href="tg://user?id={user_id}">написать в Telegram</a>'

    return (
        "🛒 <b>Новый заказ</b>\n\n"
        f"Товар: {order.product.name}\n"
        f"Цена: {format_price(order.product.price)}\n\n"
        f"Имя: {order.customer_name}\n"
        f"Телефон: {order.phone}\n"
        f"Адрес: {order.address}\n\n"
        f"Покупатель: {contact} (id {user_id})"
    )


def format_order_summary(order: Order) -> str:
    """Сводка заказа для покупателя — показываем перед подтверждением."""
    return (
        "Проверь заказ:\n\n"
        f"Товар: <b>{order.product.name}</b>\n"
        f"Цена: {format_price(order.product.price)}\n"
        f"Имя: {order.customer_name}\n"
        f"Телефон: {order.phone}\n"
        f"Адрес: {order.address}"
    )
