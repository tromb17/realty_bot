import openai
from openai import OpenAI
import os
from telegram import Update, File, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import pandas as pd

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

# ✅ Главное меню с кнопками
main_menu_keyboard = [['/start', '/menu'], ['/help', '/stop_server']]
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
        "/stop_server - Остановить сервер (только для разработчика)\n"
    )
    await update.message.reply_text(menu_text, reply_markup=reply_markup)

# ✅ Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🤖 Я бот, который использует OpenAI API для ответа на ваши вопросы.\n"
        "Вы можете отправить мне текстовое сообщение или загрузить Excel файл для обработки.\n\n"
        "🛠 Команды:\n"
        "/start - Запустить бота\n"
        "/menu - Показать меню команд\n"
        "/help - Помощь по работе с ботом\n"
        "/stop_server - Остановить сервер (только для разработчика)"
    )
    await update.message.reply_text(help_text)

# ✅ Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip()

    if not user_text:
        await update.message.reply_text("Пожалуйста, напишите сообщение.")
        return

    try:
        # 🔧 Запрос к OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=100,
            temperature=0.7
        )

        # ✅ Получение ответа и отправка пользователю
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)

    except openai.OpenAIError as e:
        logger.error(f"Ошибка API OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при подключении к OpenAI. Попробуйте позже.")
    
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        await update.message.reply_text("Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.")

# ✅ Обработчик команды /stop_server
async def stop_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Проверяем, что команду ввел разработчик
    if str(user_id) != DEVELOPER_CHAT_ID:
        await update.message.reply_text("У вас нет прав для остановки сервера.")
        return

    await update.message.reply_text("Сервер останавливается...")
    os.system("kill 1")

# ✅ Главная функция запуска бота
def main() -> None:
    logger.info("Запуск бота...")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', menu))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('stop_server', stop_server))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Запускаем бота
    application.run_polling()

# ✅ Запуск скрипта
if __name__ == '__main__':
    main()
