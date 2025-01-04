import pytz
import re
import configparser
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import nest_asyncio

# Применяем патч для поддержки asyncio в Spyder
nest_asyncio.apply()

BAD_WORDS_FILE = '/path/to/your/repository/bad_words.txt'

# Функция для загрузки списка матов
def load_bad_words():
    try:
        with open(BAD_WORDS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    except Exception as e:
        print(f"Ошибка при загрузке мата: {e}")
        return []

# Загрузите матов в переменную
BAD_WORDS = load_bad_words()

# Функция для проверки на маты
def contains_bad_words(text):
    pattern = r'\b(' + '|'.join(BAD_WORDS) + r')\b'
    return bool(re.search(pattern, text, re.IGNORECASE))

# Команда /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот и баню за маты. Давайте соблюдать правила.")

# Обработчик сообщений
async def handle_message(update: Update, context):
    message = update.message.text
    user = update.message.from_user

    if contains_bad_words(message):
        chat_id = update.message.chat.id
        user_id = user.id
        name = user.full_name

        # Проверка прав бота
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        if bot_member.status in ["administrator", "creator"]:
            try:
                # Текущее время + 10 минут
                until_time = int(time.time()) + 10 * 60  # 10 минут в секундах
                # Запрещаем отправку сообщений пользователю
                await context.bot.restrict_chat_member(
                    chat_id=chat_id, 
                    user_id=user_id, 
                    permissions={
                        "can_send_messages": False,
                        "can_send_media_messages": False,
                        "can_send_other_messages": False,
                        "can_add_web_page_previews": False
                    }
                )
                await update.message.reply_text(f"Пользователь {name} заблокирован за использование ненормативной лексики. Он не может отправлять сообщения в течении 10 минут.")
            except Exception as e:
                await update.message.reply_text(f"Ошибка при блокировке пользователя: {e}")
        else:
            await update.message.reply_text("У бота нет достаточных прав для блокировки пользователей.")

async def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    # Токен бота из файла конфигурации
    TOKEN = config['Telegram']['bot_token']

    # Создание приложения
    app = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    print("Бот запущен. Нажмите Ctrl+C для завершения.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
