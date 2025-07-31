import os
import openai
import telebot
from flask import Flask, request, jsonify
from telebot import types
from threading import Thread

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

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я ваш бот. Выберите одну из команд, чтобы продолжить.")

# Функция для обработки команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Доступные команды:
    /start - начать взаимодействие с ботом
    /help - показать помощь
    /gpt - отправить запрос в OpenAI
    /present - создать презентацию
    """
    bot.reply_to(message, help_text)

# Функция для обработки команды /gpt
@bot.message_handler(commands=['gpt'])
def gpt_prompt(message):
    msg = bot.reply_to(message, "Введите ваш запрос для OpenAI:")
    bot.register_next_step_handler(msg, handle_gpt)

def handle_gpt(message):
    user_input = message.text
    try:
        # Запрос к OpenAI для ответа
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_input,
            max_tokens=150
        )
        bot.reply_to(message, response.choices[0].text.strip())
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при запросе к OpenAI: {e}")

# Функция для создания кнопок и презентации
@bot.message_handler(commands=['present'])
def present_options(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("Создать презентацию по теме")
    item2 = types.KeyboardButton("Выбрать тему презентации")
    markup.add(item1, item2)
    bot.reply_to(message, "Выберите опцию для создания презентации", reply_markup=markup)

# Функция для обработки выбора пользователя для презентации
@bot.message_handler(func=lambda message: message.text in ["Создать презентацию по теме", "Выбрать тему презентации"])
def create_presentation(message):
    if message.text == "Создать презентацию по теме":
        bot.reply_to(message, "Введите тему для презентации")
        bot.register_next_step_handler(message, handle_presentation_topic)
    elif message.text == "Выбрать тему презентации":
        topics = ["Лев Толстой", "Математика", "История искусств"]
        markup = types.ReplyKeyboardMarkup(row_width=2)
        for topic in topics:
            markup.add(types.KeyboardButton(topic))
        bot.reply_to(message, "Выберите одну из предложенных тем", reply_markup=markup)
        bot.register_next_step_handler(message, handle_presentation_choice)

def handle_presentation_topic(message):
    topic = message.text
    bot.reply_to(message, f"Создаю презентацию на тему: {topic}")
    # Здесь можно подключить генерацию презентации (например, через python-pptx)
    bot.reply_to(message, "Презентация создана!")

def handle_presentation_choice(message):
    topic = message.text
    bot.reply_to(message, f"Создаю презентацию на тему: {topic}")
    # Здесь можно подключить генерацию презентации (например, через python-pptx)
    bot.reply_to(message, "Презентация создана!")

# Функция для обработки текстовых сообщений (фото, видео и других файлов)
@bot.message_handler(content_types=['text', 'photo', 'audio', 'document', 'video'])
def handle_all_messages(message):
    if message.content_type == 'text':
        bot.reply_to(message, "Вы отправили текстовое сообщение.")
    elif message.content_type == 'photo':
        bot.reply_to(message, "Вы отправили фото.")
    elif message.content_type == 'audio':
        bot.reply_to(message, "Вы отправили аудио.")
    elif message.content_type == 'document':
        bot.reply_to(message, "Вы отправили документ.")
    elif message.content_type == 'video':
        bot.reply_to(message, "Вы отправили видео.")

# Функция для старта бота
def start_bot():
    bot.polling(none_stop=True)

# Запуск Flask сервера
if __name__ == '__main__':
    # Запуск Telegram-бота в фоновом режиме
    thread = Thread(target=start_bot)
    thread.start()
    
    # Порт для Render
    port = int(os.environ.get('PORT', 5000))  # Render использует переменную PORT
    app.run(host='0.0.0.0', port=port)  # запуск на указанном порту
