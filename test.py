import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Получаем ключи из переменных окружения
openai.api_key = os.getenv('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот, который использует ChatGPT для ответов на ваши вопросы. Напишите что-нибудь!')

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=100
        )
        answer = response['choices'][0]['message']['content']
        await update.message.reply_text(answer)
    except openai.error.OpenAIError as e:
        logging.error(f"Ошибка API OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при подключении к OpenAI.")
    except Exception as e:
        logging.error(f"Другая ошибка: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")

# Главная функция запуска бота
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

# Запуск бота
if __name__ == '__main__':
    main()
