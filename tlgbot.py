from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import asyncio
import requests
import configparser
import nest_asyncio

# Применение nest_asyncio для поддержки вложенных событийных циклов
nest_asyncio.apply()

# Константы для шагов диалога
NAME, AGE, EMAIL = range(3)

# URL вашего сервера
SERVER_URL = "https://yourserver.com/api"

config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
bot_token = config['Telegram']['bot_token']
# ID группы, куда нужно добавлять пользователей
GROUP_ID = -1002448352331  # Замените на ID вашей группы

# Команда /start
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Привет! Пожалуйста, введите своё имя:")
    return NAME

# Получение имени
async def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Спасибо! Теперь укажите ваш возраст:")
    return AGE

# Получение возраста
async def get_age(update: Update, context: CallbackContext) -> int:
    try:
        age = int(update.message.text)
        context.user_data["age"] = age
        await update.message.reply_text("Отлично! Теперь напишите ваш email:")
        return EMAIL
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный возраст (число).")
        return AGE

# Получение email и завершение
async def get_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    context.user_data["email"] = email

    # Отправка данных на сервер
    data = {
        "name": context.user_data["name"],
        "age": context.user_data["age"],
        "email": email,
    }

    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            await update.message.reply_text("Данные успешно отправлены на сервер!")
        else:
            await update.message.reply_text("Ошибка при отправке данных на сервер.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

    # Добавление в группу через ссылку-приглашение
    try:
        # Получение ссылки-приглашения
        invite_link = await context.bot.export_chat_invite_link(chat_id=GROUP_ID)
        await update.message.reply_text(f"Присоединяйтесь к группе по ссылке: {invite_link}")
    except Exception as e:
        await update.message.reply_text(f"Не удалось создать ссылку-приглашение: {e}")

    return ConversationHandler.END

# Отмена диалога
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def main():
    # Создаём приложение
    application = Application.builder().token(bot_token).build()

    # Создаём ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
