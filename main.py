import os
import logging
import telebot
from pptx import Presentation
from pptx.util import Inches
from openai import OpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# API-ключи
BOT_TOKEN = os.getenv("8237141546:AAH4Duh0H3B7kjGn5hfu5Z4DbiaxjBY383c")
OPENAI_API_KEY = os.getenv("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")

# Инициализация бота и OpenAI клиента
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Состояние пользователей
user_state = {}

# Старт
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    user_state[user_id] = {"step": "name"}
    bot.send_message(user_id, "Привет! Я помогу создать презентацию.\nВведите одно имя или несколько?")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "name")
def handle_name(message):
    user_id = message.chat.id
    user_state[user_id]["name"] = message.text
    user_state[user_id]["step"] = "topic"
    bot.send_message(user_id, "О чём будет твоя презентация?")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "topic")
def handle_topic(message):
    user_id = message.chat.id
    user_state[user_id]["topic"] = message.text
    user_state[user_id]["step"] = "slides"
    bot.send_message(user_id, "Сколько слайдов ты хочешь? (например, 5)")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "slides")
def handle_slides(message):
    user_id = message.chat.id
    try:
        user_state[user_id]["slides"] = int(message.text)
        user_state[user_id]["step"] = "design"
        bot.send_message(user_id, "Выберите стиль дизайна:\n1 - Светлый\n2 - Классический\n3 - Темный контрастный")
    except ValueError:
        bot.send_message(user_id, "Введите число. Например, 5")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "design")
def handle_design(message):
    user_id = message.chat.id
    user_state[user_id]["design"] = message.text
    user_state[user_id]["step"] = "font"
    bot.send_message(user_id, "Выберите шрифт (например, Arial, Times New Roman):")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "font")
def handle_font(message):
    user_id = message.chat.id
    user_state[user_id]["font"] = message.text
    user_state[user_id]["step"] = "style"
    bot.send_message(user_id, "Выберите стиль контента:\nТекст\nТекст с изображением")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "style")
def handle_style(message):
    user_id = message.chat.id
    user_state[user_id]["style"] = message.text
    user_state[user_id]["step"] = "language"
    bot.send_message(user_id, "Выберите язык (например, Русский, English, Polski):")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("step") == "language")
def handle_language(message):
    user_id = message.chat.id
    user_state[user_id]["language"] = message.text

    bot.send_message(user_id, "Генерирую презентацию...")

    try:
        prs_path = generate_presentation(user_state[user_id])
        with open(prs_path, 'rb') as file:
            bot.send_document(user_id, file)
    except Exception as e:
        logger.error(f"Ошибка генерации: {e}")
        bot.send_message(user_id, f"Произошла ошибка при генерации презентации: {str(e)}")

    user_state.pop(user_id)


def generate_presentation(state):
    topic = state["topic"]
    slides = state["slides"]
    language = state["language"]

    prompt = f"Создай презентацию на тему '{topic}' на языке {language}. {slides} слайдов. Без титульного слайда. Каждый слайд в виде:\n\nЗаголовок:\nТекст:"

    # GPT-4 запрос
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content
    prs = Presentation()
    for slide_data in content.split("\n\n"):
        if "Заголовок:" in slide_data and "Текст:" in slide_data:
            title = slide_data.split("Заголовок:")[1].split("Текст:")[0].strip()
            text = slide_data.split("Текст:")[1].strip()

            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = title
            slide.placeholders[1].text = text

    file_path = "presentation.pptx"
    prs.save(file_path)
    return file_path


if __name__ == "__main__":
