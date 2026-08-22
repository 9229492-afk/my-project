"""Тесты чтения настроек — особенно на кривой ввод токена."""

import pytest

from bot.config import load_config

ТОКЕН = "8933657654:AAHnlk37c23PzZhxAUhM7X1wv9J-z56zjIM"


@pytest.fixture(autouse=True)
def чистое_окружение(monkeypatch):
    """Убираем реальные настройки, чтобы тесты не зависели от .env машины."""
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_ID", raising=False)
    monkeypatch.setattr("bot.config.load_dotenv", lambda *a, **kw: None)


def test_токен_читается(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", ТОКЕН)
    assert load_config().bot_token == ТОКЕН


@pytest.mark.parametrize(
    "лишнее", [f" {ТОКЕН}", f"{ТОКЕН} ", f"{ТОКЕН}\n", f"\t{ТОКЕН}\n"]
)
def test_пробелы_по_краям_срезаются(monkeypatch, лишнее):
    """При копировании в конец часто попадает пробел или перенос строки."""
    monkeypatch.setenv("BOT_TOKEN", лишнее)
    assert load_config().bot_token == ТОКЕН


def test_пробел_внутри_токена_даёт_понятную_ошибку(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "8933657654:AAH nlk37c23")

    with pytest.raises(RuntimeError, match="пробел"):
        load_config()


def test_пустой_токен_отклоняется(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "   ")

    with pytest.raises(RuntimeError, match="Не найден BOT_TOKEN"):
        load_config()


def test_без_admin_id_бот_всё_равно_поднимается(monkeypatch):
    """Иначе нельзя было бы запустить бота, чтобы узнать свой ID командой /id."""
    monkeypatch.setenv("BOT_TOKEN", ТОКЕН)
    assert load_config().admin_id is None


def test_admin_id_читается_числом(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", ТОКЕН)
    monkeypatch.setenv("ADMIN_ID", "5258722824")
    assert load_config().admin_id == 5258722824


def test_username_вместо_admin_id_отклоняется(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", ТОКЕН)
    monkeypatch.setenv("ADMIN_ID", "@vasya")

    with pytest.raises(RuntimeError, match="числом"):
        load_config()
