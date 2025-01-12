import openai
from openai import OpenAI
import os
from telegram import Update, File
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

# ✅ Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот ChatGPT. Вы можете отправить мне Excel файл для обработки.')

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

# ✅ Обработчик документов (Excel файлов)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document

    # Проверяем, что файл является Excel файлом
    if document.mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
        # Скачиваем файл во временную папку
        file: File = await context.bot.get_file(document.file_id)
        file_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(file_path)

        # ✅ Отправляем файл разработчику
        with open(file_path, 'rb') as f:
            await context.bot.send_document(chat_id=477555112, document=f)
        
        # ✅ Сообщаем пользователю об успешной загрузке
        await update.message.reply_text("Файл загружен и отправлен разработчику.")
    else:
        await update.message.reply_text("Пожалуйста, отправьте Excel файл в формате .xlsx или .xls.")

# ✅ Главная функция запуска бота
def main() -> None:
    logger.info("Запуск бота...")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Запускаем бота
    application.run_polling()

# ✅ Запуск скрипта
if __name__ == '__main__':
    main()



