import random
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

# --- ТОКЕНЫ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_API_KEY = os.environ.get("HF_API_KEY")

# --- НАСТРОЙКА МОЗГА (HUGGING FACE) ---
client = InferenceClient(provider="hf-inference", api_key=HF_API_KEY)

# Память для каждого пользователя, чтобы бот помнил контекст
user_conversations = {}

# --- ЛОКАЦИИ И РЫБА (оставляем как было) ---
LOCATIONS = [
    "Пискаревка", "Академический пруд", "Нева у моста", "Мусорка за домом",
    "База под мостом", "Крыша у Артёма", "Фонтан в парке", "Заброшенный пирс",
    "Старый пруд у школы", "Речка за гаражами", "Озеро в лесу", "Канал у завода"
]
FISHES = [
    ("Окунь", "300 г"), ("Карась", "500 г"), ("Щука", "1.5 кг"),
    ("Лещ", "800 г"), ("Плотва", "200 г"), ("Сом", "3 кг"),
    ("Карп", "2.5 кг"), ("Судак", "1.2 кг"), ("Ерш", "150 г"),
    ("Голавль", "600 г"), ("Язь", "900 г"), ("Линь", "700 г")
]

# --- КНОПКИ ---
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Рыбалка"), KeyboardButton("Болталка")],
         [KeyboardButton("Куда пойти")]],
        resize_keyboard=True
    )

def get_location_keyboard():
    buttons = [[KeyboardButton(loc)] for loc in LOCATIONS]
    buttons.append([KeyboardButton("Назад")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_fish_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Рыбалка")], [KeyboardButton("Назад")]],
        resize_keyboard=True
    )

# --- ФУНКЦИЯ ОБЩЕНИЯ С ИИ ---
def ask_ai(user_id, text):
    # Если у пользователя ещё нет истории — создаём
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    # Добавляем сообщение пользователя
    user_conversations[user_id].append({"role": "user", "content": text})

    # Ограничиваем историю последними 10 сообщениями
    if len(user_conversations[user_id]) > 10:
        user_conversations[user_id] = user_conversations[user_id][-10:]

    try:
        # Запрос к нейросети
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=user_conversations[user_id],
            max_tokens=500,
            temperature=0.7,
        )
        response_text = completion.choices[0].message.content
        # Добавляем ответ бота в историю
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
        # --- ЗДЕСЬ ОТВЕЧАЕТ ИИ ---
        ai_response = ask_ai(user_id, text)
        await update.message.reply_text(ai_response, reply_markup=get_main_keyboard())

# --- ЗАПУСК ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
    
