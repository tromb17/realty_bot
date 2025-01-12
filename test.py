import openai
import os

# Укажите свой API-ключ
openai.api_key = os.getenv("OPENAI_API_KEY")

# Пример запроса к модели GPT
response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Привет! Как тебя зовут?"}
    ],
    max_tokens=10
)

# Выводим ответ
print(response['choices'][0]['message']['content'])
