import random
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

# Вставь сюда свой токен от BotFather
BOT_TOKEN = "8720154823:AAGgoLl13YBEPVAKACb3o3rjsOhdr0t9Ve4"

# Адрес прокси. Это HTTP-прокси, который я нашел в открытых списках.
# Если не сработает, попробуем другой.
PROXY_URL = "http://1.12.220.206:2080"

LOCATIONS = ["Пискаревка", "Академический пруд", "Нева у моста", "Мусорка за домом"]

FISHES = [
    ("Окунь", "300 г"),
    ("Карась", "500 г"),
    ("Щука", "1.5 кг"),
    ("Лещ", "800 г"),
    ("Плотва", "200 г"),
    ("Сом", "3 кг"),
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Рыбалка"), KeyboardButton("Болталка")],
        [KeyboardButton("Куда пойти")]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Йо, Чувак! Выбирай:", reply_markup=markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Рыбалка":
        keyboard = [[KeyboardButton(loc)] for loc in LOCATIONS]
        keyboard.append([KeyboardButton("Назад")])
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Куда пойдём?", reply_markup=markup)

    elif text == "Болталка":
        await update.message.reply_text("О чём хочешь поговорить? Просто пиши.")

    elif text == "Куда пойти":
        await update.message.reply_text("Мест много: парк, мост, база, крыша. Куда хочешь?")

    elif text in LOCATIONS:
        fish, weight = random.choice(FISHES)
        await update.message.reply_text(
            f"Ты пошёл на {text} и поймал {fish} весом {weight}!",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Рыбалка")], [KeyboardButton("Назад")]], resize_keyboard=True)
        )

    elif text == "Назад":
        await start(update, context)

    else:
        await update.message.reply_text("Интересно, расскажи ещё.")

if __name__ == '__main__':
    # Если используешь SOCKS5, нужно установить библиотеку: pip install "python-telegram-bot[socks]"
    # Для HTTP-прокси вроде этого, вроде, ничего дополнительного не нужно.
    request = HTTPXRequest(proxy=PROXY_URL)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).get_updates_request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()