import logging
import os
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования (чтобы видеть ошибки в Render)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- ТОКЕНЫ И НАСТРОЙКИ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# Render сам подставит свой URL в эту переменную, если мы ее добавим
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
# Render дает порт через переменную окружения, по умолчанию 10000
PORT = int(os.environ.get("PORT", 10000))

# --- ДАННЫЕ ДЛЯ БОТА ---
LOCATIONS = ["Пискаревка", "Академический пруд", "Нева у моста", "Мусорка за домом", "База под мостом", "Крыша у Артёма"]
FISHES = [("Окунь", "300 г"), ("Карась", "500 г"), ("Щука", "1.5 кг"), ("Лещ", "800 г"), ("Плотва", "200 г"), ("Сом", "3 кг"), ("Карп", "2.5 кг"), ("Судак", "1.2 кг")]
TALK_RESPONSES = ["Интересно, расскажи ещё.", "А что было дальше?", "Жёстко, брат.", "Ну ты даёшь.", "Слушай, а что потом?", "Понял тебя.", "Это сильно.", "Давай подробнее.", "Хм, а почему так?", "Ого, вот это поворот."]

# --- КНОПКИ ---
def get_main_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("Рыбалка"), KeyboardButton("Болталка")], [KeyboardButton("Куда пойти")]], resize_keyboard=True)

def get_location_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton(loc)] for loc in LOCATIONS] + [[KeyboardButton("Назад")]], resize_keyboard=True)

def get_fish_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("Рыбалка")], [KeyboardButton("Назад")]], resize_keyboard=True)

# --- ЛОГИКА БОТА ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Йо, Чувак! Выбирай:", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
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
        await update.message.reply_text(random.choice(TALK_RESPONSES), reply_markup=get_main_keyboard())

# --- ЗАПУСК ВЕБ-ХУКА ---
if __name__ == '__main__':
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен!")
    elif not WEBHOOK_URL:
        logger.error("WEBHOOK_URL не установлен! Добавь его в Render.")
    else:
        # Создаем приложение
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Запускаем веб-хук
        logger.info(f"Запуск веб-хука на порту {PORT}...")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=f"{WEBHOOK_URL}/webhook"
        )
