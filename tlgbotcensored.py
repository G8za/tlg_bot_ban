import pytz
import re
import configparser
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import nest_asyncio

# Применяем патч для поддержки asyncio в Spyder
nest_asyncio.apply()

# Список слов, считающихся ненормативной лексикой
BAD_WORDS = ["нахуй", "ебаная", "пизда", "хуя", "залупа", "гандон", "ебал", "хуила", "пидорас"]  # Замените на реальные маты

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
                await update.message.reply_text(f"Пользователь {name} заблокирован за использование ненормативной лексики. Он не может отправлять сообщения.")
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
