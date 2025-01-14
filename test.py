import openai
from openai import OpenAI
import os
from telegram import Update, File, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import pandas as pd
import requests  # 📌 Для работы с веб-запросами

# ✅ Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ✅ Получаем ключи из переменных окружения
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DEVELOPER_CHAT_ID = os.getenv('DEVELOPER_CHAT_ID')

if not OPENAI_API_KEY or not TELEGRAM_TOKEN or not DEVELOPER_CHAT_ID:
    raise ValueError("Необходимо задать переменные окружения OPENAI_API_KEY, TELEGRAM_TOKEN и DEVELOPER_CHAT_ID")

# ✅ Инициализация OpenAI клиента
openai.api_key = OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Ссылка на веб-приложение Google Apps Script
GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyVQo3NCKrtjHahNomfj0QjCiDVq_y3DW0naLc4AzuVAkoCSOAe5igPFg93FiZz-ldLmg/exec"

# ✅ Главное меню с кнопками
main_menu_keyboard = [['/start', '/menu'], ['/help', '/upload'], ['/stop_server']]
reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

# ✅ Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я бот ChatGPT. Вот список доступных команд:',
        reply_markup=reply_markup
    )

# ✅ Обработчик команды /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_text = (
        "📋 Доступные команды:\n"
        "/start - Запустить бота\n"
        "/menu - Показать меню команд\n"
        "/help - Помощь по работе с ботом\n"
        "/upload - Загрузить файл для обработки\n"
        "/stop_server - Остановить сервер (только для разработчика)\n"
    )
    await update.message.reply_text(menu_text, reply_markup=reply_markup)

# ✅ Обработчик текстового запроса "выведи <номер> строку"
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip().lower()

    if "выведи" in user_text and "строку" in user_text:
        try:
            # Получаем номер строки из сообщения пользователя
            row_number = int(user_text.split()[1])

            # Запрос к веб-приложению Apps Script
            response = requests.get(GOOGLE_APPS_SCRIPT_URL)
            response.raise_for_status()

            # Преобразуем данные из JSON
            data = response.json()

            # Проверяем, что запрашиваемая строка существует
            if row_number <= len(data):
                row_data = data[row_number - 1]
                message = f"📊 Данные из строки {row_number}:\n" + ", ".join(map(str, row_data))
            else:
                message = f"Строка {row_number} не найдена в таблице."

            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}")
            await update.message.reply_text("Произошла ошибка при получении данных из таблицы. Проверьте запрос.")
    else:
        await update.message.reply_text("Пожалуйста, сформулируйте запрос в формате: 'выведи <номер> строку'.")

# ✅ Главная функция запуска бота
def main() -> None:
    logger.info("Запуск бота...")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Запускаем бота
    application.run_polling()

# ✅ Запуск скрипта
if __name__ == '__main__':
    main()
