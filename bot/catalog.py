"""Каталог товаров и всё, что с ним связано.

Здесь нет ни одной строчки, связанной с Telegram, — только данные и логика.
Поэтому эти функции можно проверять тестами, не запуская бота (см. tests/).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    """Один товар в каталоге."""

    id: str
    name: str
    price: int  # цена в рублях, целое число
    description: str
    # Фотография: file_id Telegram или ссылка на картинку. None — товар
    # покажется текстом. Самый простой способ получить file_id: отправить
    # фото боту и посмотреть его в логе.
    photo: str | None = None


# ЗАМЕНИ на свои товары. Пока это заглушка, чтобы каталог было видно в боте.
# Когда товаров станет много или их нужно будет менять без правки кода —
# переедем отсюда в базу данных.
PRODUCTS: tuple[Product, ...] = (
    Product(
        id="cup",
        name="Кружка",
        price=590,
        description="Керамическая кружка, 350 мл. Можно мыть в посудомойке.",
    ),
    Product(
        id="tshirt",
        name="Футболка",
        price=1490,
        description="Хлопок 100%, размеры S–XL.",
    ),
    Product(
        id="sticker-pack",
        name="Набор стикеров",
        price=250,
        description="12 виниловых стикеров, не выгорают на солнце.",
    ),
)


def all_products() -> tuple[Product, ...]:
    """Все товары каталога."""
    return PRODUCTS


def find_product(product_id: str) -> Product | None:
    """Найти товар по id. Возвращает None, если такого товара нет."""
    for product in PRODUCTS:
        if product.id == product_id:
            return product
    return None


def format_price(price: int) -> str:
    """Цена в виде '1 490 ₽' — с пробелом между тысячами."""
    return f"{price:,}".replace(",", " ") + " ₽"


def format_product(product: Product) -> str:
    """Текст карточки товара для отправки в чат (разметка HTML)."""
    return (
        f"<b>{product.name}</b>\n\n"
        f"{product.description}\n\n"
        f"Цена: {format_price(product.price)}"
    )
