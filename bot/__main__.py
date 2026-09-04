"""Точка входа: запуск бота командой `python -m bot`."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError

from bot.config import Config, load_config
from bot.handlers import catalog, legal, order, start
from bot.middlewares import LogUserMiddleware

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

    # outer_middleware срабатывает до фильтров, то есть на любой апдейт,
    # даже если под него нет ни одного обработчика.
    dispatcher.update.outer_middleware(LogUserMiddleware())

    dispatcher.include_router(start.router)
    dispatcher.include_router(catalog.router)
    dispatcher.include_router(order.router)
    dispatcher.include_router(legal.router)

    # Сбрасываем накопившиеся апдейты: иначе после долгого простоя бот
    # начнёт отвечать на сообщения недельной давности.
    await bot.delete_webhook(drop_pending_updates=True)

    await проверить_связь_с_владельцем(bot, config)

    logger.info("Бот запущен")
    await dispatcher.start_polling(bot)


async def проверить_связь_с_владельцем(bot: Bot, config: Config) -> None:
    """Сразу проверить, доходят ли сообщения до владельца магазина.

    Без этой проверки неверный ADMIN_ID обнаруживается только когда
    покупатель оформит заказ и тот не дойдёт. Лучше узнать при запуске.
    """
    if config.admin_id is None:
        logger.warning(
            "ADMIN_ID не заполнен — заказы будут попадать только в лог. "
            "Отправь боту команду /id и впиши полученное число в ADMIN_ID."
        )
        return

    try:
        await bot.send_message(
            config.admin_id,
            "✅ Бот запущен и готов принимать заказы.\n\n"
            "Раз ты видишь это сообщение — ADMIN_ID указан верно, "
            "заказы будут приходить сюда.",
        )
    except TelegramAPIError as error:
        logger.error(
            "НЕ УДАЛОСЬ НАПИСАТЬ ВЛАДЕЛЬЦУ (ADMIN_ID=%s): %s\n"
            "Заказы до тебя доходить НЕ БУДУТ. Две возможные причины:\n"
            "  1. ADMIN_ID неверный — отправь боту /id и сверь число\n"
            "  2. Владелец ни разу не писал боту — открой чат и нажми «Запустить»",
            config.admin_id,
            error,
        )
        return

    logger.info("Владелец на связи: ADMIN_ID=%s, сообщение доставлено", config.admin_id)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
