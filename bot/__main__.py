"""Точка входа: запуск бота командой `python -m bot`."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import load_config
from bot.handlers import catalog, order, start

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = load_config()

    # parse_mode=HTML — чтобы <b>жирный</b> в текстах работал везде,
    # не указывая parse_mode в каждой отправке отдельно.
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Всё, что передано в Dispatcher(...), aiogram подставит в обработчики
    # по имени аргумента — так config попадает в accept_order.
    dispatcher = Dispatcher(config=config)
    dispatcher.include_router(start.router)
    dispatcher.include_router(catalog.router)
    dispatcher.include_router(order.router)

    # Сбрасываем накопившиеся апдейты: иначе после долгого простоя бот
    # начнёт отвечать на сообщения недельной давности.
    await bot.delete_webhook(drop_pending_updates=True)

    if config.admin_id is None:
        logger.warning(
            "ADMIN_ID не заполнен — заказы будут попадать только в лог. "
            "Отправь боту команду /id, впиши число в .env и перезапусти."
        )

    logger.info("Бот запущен")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
