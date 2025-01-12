import openai

# Укажите свой API-ключ
openai.api_key = "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"

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
