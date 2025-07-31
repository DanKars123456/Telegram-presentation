import telebot
import openai
from pptx import Presentation
import os
import logging

# === Настройки ===
TELEGRAM_TOKEN = '8237141546:AAH4Duh0H3B7kjGn5hfu5Z4DbiaxjBY383c'  # Укажите свой Telegram токен
OPENAI_API_KEY = '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'  # Укажите свой OpenAI API ключ
openai.api_key = OPENAI_API_KEY

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Логирование
logging.basicConfig(level=logging.INFO)

# Хранение состояния пользователей
user_states = {}

# === Дизайны (ключ -> имя дизайна) ===
designs = {
    "1": "Яркий современный",
    "2": "Минимализм",
    "3": "Темный контрастный",
    "4": "Пастельный эстетичный"
}

# === Шрифты (для выбора пользователем) ===
fonts = [
    "Arial", "Calibri", "Times New Roman", "Verdana", "Courier New", "Georgia", "Comic Sans MS"
]

# === Стили контента ===
content_styles = [
    "Только текст",
    "Текст с изображением",
    "Список с пунктами",
    "Текст с графиками"
]

# === Обработка команды /start ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    logging.info(f"Received /start from {message.chat.id}")  # Логируем команду /start

    bot.send_message(message.chat.id, "Привет! Я помогу создать презентацию.")

    # Инициализация состояния пользователя
    user_states[message.chat.id] = {"step": "name_choice"}

    # Предложение выбрать одно или несколько имен
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("1 имя", "Несколько имен")
    bot.send_message(message.chat.id, "Введите одно имя или несколько?", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    logging.info(f"Received message: {message.text} from {message.chat.id}")  # Логируем все сообщения

    state = user_states.get(message.chat.id, {})
    step = state.get("step")
    logging.info(f"User state: {state}")

    if step == "name_choice":
        if message.text == "1 имя":
            state["step"] = "name"
            bot.send_message(message.chat.id, "Какое имя будет в презентации?")

        elif message.text == "Несколько имен":
            state["step"] = "how_many_names"
            bot.send_message(message.chat.id, "Сколько имен ты хочешь добавить?")

    elif step == "name":
        state["name"] = message.text
        state["step"] = "topic"
        bot.send_message(message.chat.id, f"Приятно познакомиться, {message.text}! О чём будет твоя презентация?")

    elif step == "how_many_names":
        if message.text.isdigit():
            state["how_many"] = int(message.text)
            state["names"] = []
            state["step"] = "collecting_names"
            bot.send_message(message.chat.id, f"Отлично! Пожалуйста, введи имя и фамилию 1 из {state['how_many']}")
        else:
            bot.send_message(message.chat.id, "Пожалуйста, введите число.")

    elif step == "collecting_names":
        if len(message.text.split()) < 2:
            bot.send_message(message.chat.id, "Пожалуйста, укажите имя и фамилию.")
        else:
            state["names"].append(message.text)
            if len(state["names"]) == state["how_many"]:
                state["step"] = "topic"
                bot.send_message(message.chat.id, "О чём будет твоя презентация?")
            else:
                next_index = len(state["names"]) + 1
                bot.send_message(message.chat.id, f"Введите имя и фамилию {next_index} из {state['how_many']}")

    elif step == "topic":
        state["topic"] = message.text
        state["step"] = "slides"
        bot.send_message(message.chat.id, "Сколько слайдов ты хочешь? (Например, 5)")

    elif step == "slides":
        if message.text.isdigit():
            state["slides"] = int(message.text)
            state["step"] = "design"
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for k, v in designs.items():
                markup.add(f"{k} - {v}")
            bot.send_message(message.chat.id, "Выберите стиль дизайна:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Введите число.")

    elif step == "design":
        key = message.text.split(" ")[0]
        if key in designs:
            state["design"] = designs[key]
            state["step"] = "font"
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for f in fonts:
                markup.add(f)
            bot.send_message(message.chat.id, "Выберите шрифт:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, выберите один из предложенных вариантов.")

    elif step == "font":
        if message.text in fonts:
            state["font"] = message.text
            state["step"] = "style"
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for s in content_styles:
                markup.add(s)
            bot.send_message(message.chat.id, "Выберите стиль контента:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, выберите из списка.")

    elif step == "style":
        if message.text in content_styles:
            state["style"] = message.text
            state["step"] = "language"
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            langs = ["Русский", "English", "Polski", "Deutsch"]
            for l in langs:
                markup.add(l)
            bot.send_message(message.chat.id, "Выберите язык:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Выберите вариант из предложенных.")

    elif step == "language":
        state["language"] = message.text
        bot.send_message(message.chat.id, "Генерирую презентацию...")
        try:
            content = generate_text(state["topic"], state["slides"], state["language"])
            filename = create_ppt(state, content)
            with open(filename, 'rb') as f:
                bot.send_document(message.chat.id, f)
            os.remove(filename)
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {e}")

# === Генерация текста презентации ===
from openai import OpenAIError  # добавь это вверху main.py вместе с другими импортами

def generate_and_send_presentation(message):
    state = user_states[message.chat.id]
    bot.send_message(message.chat.id, "Генерирую презентацию...")

    try:
        text = generate_text(state["topic"], state["slides"], state["language"])
        file_path = create_pptx(state["topic"], text, ", ".join(state["names"]), state["design"], state["font"], state["content_style"])
        bot.send_document(message.chat.id, open(file_path, 'rb'))
        os.remove(file_path)
    except OpenAIError as e:
        bot.send_message(message.chat.id, f"Ошибка OpenAI: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
        )
    return response.choices[0].message.content

# === Создание презентации ===
def create_ppt(state, text):
    prs = Presentation()
    slides = text.strip().split("\n")
    for s in slides:
        if ':' in s:
            title, content = s.split(':', 1)
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = title.strip()
            slide.placeholders[1].text = content.strip()

    filename = f"presentation_{state['topic'].replace(' ', '_')}.pptx"
    prs.save(filename)
    return filename
# === Запуск бота ===
bot.polling(none_stop=True)
