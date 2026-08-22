#!/usr/bin/env bash
# Запускается автоматически один раз при старте Codespace (см. devcontainer.json,
# postStartCommand — срабатывает при старте контейнера, а не при каждом подключении,
# поэтому повторные заходы в Codespace не создают вторую копию бота).
# Смысл: чтобы бота можно было поднять с телефона, ничего не набирая в терминале.

set -u

# Защита от повторного запуска, если скрипт всё же вызвали руками ещё раз.
if pgrep -f "python -m bot" > /dev/null 2>&1; then
    echo "ℹ️  Бот уже запущен в этом Codespace — второй экземпляр не поднимаю."
    echo "   Проверить: ps aux | grep bot   Остановить: pkill -f \"python -m bot\""
    exit 0
fi

if [ -n "${BOT_TOKEN:-}" ]; then
    echo "✅ BOT_TOKEN найден — запускаю бота..."
    echo "   Остановить: Ctrl+C. Запустить снова: python -m bot"
    echo
    exec python -m bot
fi

# Токена нет — не падаем молча, а объясняем, что делать.
cat <<'MESSAGE'
⚠️  Бот не запущен: не задан BOT_TOKEN.

Как это исправить, не набирая ничего в терминале:

  1. На github.com: Settings → Codespaces → New secret
  2. Создай два секрета, для обоих Repository access → my-project:
        BOT_TOKEN  — токен от @BotFather
        ADMIN_ID   — твой Telegram ID (узнаётся командой /id у бота)
  3. Удали этот codespace и создай заново — секреты подхватываются
     только при создании.

После этого бот запустится сам, и здесь появится строка «Бот запущен».
MESSAGE
