import random
import os
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

# --- ТОКЕНЫ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_API_KEY = os.environ.get("HF_API_KEY")

# --- ФЕЙКОВЫЙ ВЕБ-СЕРВЕР ДЛЯ RENDER ---
web_app = Flask(__name__)

@web_app.route('/')
def health():
    return "Bot is running"

@web_app.route('/health')
def health_check():
    return "OK"

# --- НАСТРОЙКА HUGGING FACE ---
client = InferenceClient(provider="hf-inference", api_key=HF_API_KEY)
user_conversations = {}

# --- ЛОКАЦИИ И РЫБА (оставляем как было) ---
LOCATIONS = ["Пискаревка", "Академический пруд", "Нева у моста", "Мусорка за домом", "База под мостом", "Крыша у Артёма"]
FISHES = [("Окунь", "300 г"), ("Карась", "500 г"), ("Щука", "1.5 кг"), ("Лещ", "800 г"), ("Плотва", "200 г"), ("Сом", "3 кг"), ("Карп", "2.5 кг"), ("Судак", "1.2 кг")]

# --- КНОПКИ ---
MAIN_KEYBOARD = [[KeyboardButton("Рыбалка"), KeyboardButton("Болталка")], [KeyboardButton("Куда пойти")]]
def get_main_keyboard(): return ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
def get_location_keyboard(): return ReplyKeyboardMarkup([[KeyboardButton(loc)] for loc in LOCATIONS] + [[KeyboardButton("Назад")]], resize_keyboard=True)
def get_fish_keyboard(): return ReplyKeyboardMarkup([[KeyboardButton("Рыбалка")], [KeyboardButton("Назад")]], resize_keyboard=True)

# --- ФУНКЦИЯ ДЛЯ ИИ ---
def ask_ai(user_id, text):
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    user_conversations[user_id].append({"role": "user", "content": text})
    if len(user_conversations[user_id]) > 10:
        user_conversations[user_id] = user_conversations[user_id][-10:]
    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
            messages=user_conversations[user_id],
            max_tokens=500,
            temperature=0.7,
        )
        response_text = completion.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": response_text})
        return response_text
    except Exception as e:
        return f"Ошибка ИИ: {e}"

# --- ЛОГИКА БОТА ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Йо, Чувак! Выбирай:", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.chat_id

    if text == "Рыбалка":
        await update.message.reply_text("Куда пойдём?", reply_markup=get_location_keyboard())
    elif text == "Болталка":
        await update.message.reply_text("О чём хочешь поговорить? Просто пиши.", reply_markup=get_main_keyboard())
    elif text == "Куда пойти":
        await update.message.reply_text("Мест много: парк, мост, база, крыша. Куда хочешь?", reply_markup=get_main_keyboard())
    elif text in LOCATIONS:
        fish, weight = random.choice(FISHES)
        await update.message.reply_text(f"Ты пошёл на {text} и поймал {fish} весом {weight}!", reply_markup=get_fish_keyboard())
    elif text == "Назад":
        await start(update, context)
    else:
        ai_response = ask_ai(user_id, text)
        await update.message.reply_text(ai_response, reply_markup=get_main_keyboard())

# --- ЗАПУСК ВСЕГО ---
def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    Thread(target=run_bot).start()
    # Запускаем Flask-сервер, чтобы Render видел порт
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)
