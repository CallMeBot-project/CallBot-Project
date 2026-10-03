import random
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Токен берётся из переменной окружения на Render
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8720154823:AAGgoLl13YBEPVAKACb3o3rjsOhdr0t9Ve4")

# --- ЛОКАЦИИ ДЛЯ РЫБАЛКИ ---
LOCATIONS = [
    "Пискаревка",
    "Академический пруд",
    "Нева у моста",
    "Мусорка за домом",
    "База под мостом",
    "Крыша у Артёма"
]

# --- РЫБА (название, вес) ---
FISHES = [
    ("Окунь", "300 г"),
    ("Карась", "500 г"),
    ("Щука", "1.5 кг"),
    ("Лещ", "800 г"),
    ("Плотва", "200 г"),
    ("Сом", "3 кг"),
    ("Карп", "2.5 кг"),
    ("Судак", "1.2 кг"),
]

# --- БОЛТАЛКА (ответы на слова) ---
TALK_RESPONSES = [
    "Интересно, расскажи ещё.",
    "А что было дальше?",
    "Жёстко, брат.",
    "Ну ты даёшь.",
    "Слушай, а что потом?",
    "Понял тебя.",
    "Это сильно.",
    "Давай подробнее.",
    "Хм, а почему так?",
    "Ого, вот это поворот.",
]

# --- КНОПКИ ---
MAIN_KEYBOARD = [
    [KeyboardButton("Рыбалка"), KeyboardButton("Болталка")],
    [KeyboardButton("Куда пойти")]
]

def get_main_keyboard():
    return ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

def get_location_keyboard():
    keyboard = [[KeyboardButton(loc)] for loc in LOCATIONS]
    keyboard.append([KeyboardButton("Назад")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_fish_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Рыбалка")], [KeyboardButton("Назад")]],
        resize_keyboard=True
    )

# --- СТАРТ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Йо, Чувак! Выбирай:",
        reply_markup=get_main_keyboard()
    )

# --- ОБРАБОТКА СООБЩЕНИЙ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Рыбалка":
        await update.message.reply_text(
            "Куда пойдём?",
            reply_markup=get_location_keyboard()
        )

    elif text == "Болталка":
        await update.message.reply_text(
            "О чём хочешь поговорить? Просто пиши.",
            reply_markup=get_main_keyboard()
        )

    elif text == "Куда пойти":
        await update.message.reply_text(
            "Мест много: парк, мост, база, крыша. Куда хочешь?",
            reply_markup=get_main_keyboard()
        )

    elif text in LOCATIONS:
        fish, weight = random.choice(FISHES)
        await update.message.reply_text(
            f"Ты пошёл на {text} и поймал {fish} весом {weight}!",
            reply_markup=get_fish_keyboard()
        )

    elif text == "Назад":
        await start(update, context)

    else:
        # --- БОЛТАЛКА: отвечает на любые слова ---
        response = random.choice(TALK_RESPONSES)
        await update.message.reply_text(response, reply_markup=get_main_keyboard())

# --- ЗАПУСК ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
