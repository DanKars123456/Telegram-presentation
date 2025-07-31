import os
import openai
import telebot
from flask import Flask, request, jsonify
from telebot import types

# Настройки
app = Flask(__name__)

# Токены и API
TELEGRAM_TOKEN = os.getenv('8237141546:AAH4Duh0H3B7kjGn5hfu5Z4DbiaxjBY383c')
OPENAI_API_KEY = os.getenv('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')

# Инициализация Telegram бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Главная страница веб-сервера
@app.route('/')
def home():
    return "Hello, this is the bot server!"

# Функция для обработки сообщений
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я ваш бот. Напишите что-нибудь, чтобы я ответил.")

# Функция для обработки всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Получение текста от пользователя
        user_message = message.text
        
        # Запрос к OpenAI для ответа
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )

        # Ответ от OpenAI
        bot.reply_to(message, response.choices[0].text.strip())
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Функция для старта бота
def start_bot():
    bot.polling(none_stop=True)

# Запуск Flask сервера
if __name__ == '__main__':
    # Запуск Flask в фоновом режиме
    from threading import Thread
    thread = Thread(target=start_bot)
    thread.start()
    
    # Порт для Render
    port = int(os.environ.get('PORT', 5000))  # Render использует переменную PORT
    app.run(host='0.0.0.0', port=port)  # запуск на указанном порту
