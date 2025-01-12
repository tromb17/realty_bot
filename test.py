import openai
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# ✅ Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ✅ Получаем ключи из переменных окружения
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not OPENAI_API_KEY or not TELEGRAM_TOKEN:
    raise ValueError("Необходимо задать переменные окружения OPENAI_API_KEY и TELEGRAM_TOKEN")

openai.api_key = OPENAI_API_KEY

# ✅ Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот ChatGPT. Задавайте ваши вопросы.')

# ✅ Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip()

    if not user_text:
        await update.message.reply_text("Пожалуйста, напишите сообщение.")
        return

    try:
        # 🔧 Запрос к OpenAI API (с использованием openai.chat.completions.create())
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=100,
            temperature=0.7
        )

        # ✅ Получение ответа и отправка пользователю
        answer = response['choices'][0]['message']['content'].strip()
        await update.message.reply_text(answer)

    except openai.OpenAIError as e:
        logger.error(f"Ошибка API OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при подключении к OpenAI. Попробуйте позже.")
    
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        await update.message.reply_text("Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.")

# ✅ Главная функция запуска бота
def main() -> None:
    logger.info("Запуск бота...")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()

# ✅ Запуск скрипта
if __name__ == '__main__':
    main()
