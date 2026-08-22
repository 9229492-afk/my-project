"""Тесты логики заказа — без Telegram и без токена."""

import pytest

from bot.catalog import find_product
from bot.orders import (
    Order,
    clean_address,
    clean_name,
    format_order_for_admin,
    format_order_summary,
    normalize_phone,
)


@pytest.fixture
def заказ() -> Order:
    product = find_product("cup")
    assert product is not None
    return Order(
        product=product,
        customer_name="Иван Петров",
        phone="+79991234567",
        address="Химки, ул. Ленина, 5",
    )


@pytest.mark.parametrize(
    "введено, ожидается",
    [
        ("8 (999) 123-45-67", "+79991234567"),
        ("+7 999 123 45 67", "+79991234567"),
        ("79991234567", "+79991234567"),
        ("9991234567", "+79991234567"),  # без кода страны
    ],
)
def test_телефон_приводится_к_единому_виду(введено, ожидается):
    assert normalize_phone(введено) == ожидается


@pytest.mark.parametrize("мусор", ["", "телефона нет", "123", "1" * 20])
def test_некорректный_телефон_отклоняется(мусор):
    assert normalize_phone(мусор) is None


def test_имя_очищается_от_лишних_пробелов():
    assert clean_name("  Иван   Петров \n") == "Иван Петров"


@pytest.mark.parametrize("мусор", ["", "я", "12345", "???"])
def test_некорректное_имя_отклоняется(мусор):
    assert clean_name(мусор) is None


def test_короткий_адрес_отклоняется():
    assert clean_address("дом") is None
    assert clean_address("Химки, ул. Ленина, 5") == "Химки, ул. Ленина, 5"


def test_в_заказе_для_админа_есть_все_данные(заказ):
    text = format_order_for_admin(заказ, user_id=42, username="ivan")

    assert заказ.customer_name in text
    assert заказ.phone in text
    assert заказ.address in text
    assert заказ.product.name in text
    assert "@ivan" in text


def test_без_username_даётся_ссылка_на_профиль(заказ):
    text = format_order_for_admin(заказ, user_id=42, username=None)

    assert "tg://user?id=42" in text
    assert "@" not in text


def test_сводка_для_покупателя_содержит_заказ(заказ):
    text = format_order_summary(заказ)

    assert заказ.product.name in text
    assert заказ.phone in text
    assert заказ.address in text
