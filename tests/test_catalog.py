"""Тесты логики каталога — запускаются без Telegram и без токена."""

from bot.catalog import (
    PRODUCTS,
    all_products,
    find_product,
    format_price,
    format_product,
)


def test_каталог_не_пустой():
    assert len(all_products()) > 0


def test_у_товаров_уникальные_id():
    ids = [product.id for product in PRODUCTS]
    assert len(ids) == len(set(ids)), "Два товара с одинаковым id — кнопки перепутаются"


def test_найти_существующий_товар():
    product = all_products()[0]
    assert find_product(product.id) == product


def test_несуществующий_товар_возвращает_none():
    assert find_product("такого-товара-нет") is None


def test_цена_с_разделителем_тысяч():
    assert format_price(1490) == "1 490 ₽"
    assert format_price(250) == "250 ₽"


def test_в_карточке_есть_название_и_цена():
    product = find_product("cup")
    assert product is not None

    card = format_product(product)
    assert product.name in card
    assert format_price(product.price) in card
