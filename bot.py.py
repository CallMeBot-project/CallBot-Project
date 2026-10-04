import random
import os
import asyncio
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

# --- ТОКЕН И ПОРТ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# --- ЛОКАЦИИ ДЛЯ РЫБАЛКИ ---
LOCATIONS = [
    "Пискаревка", "Академический пруд", "Нева у моста", "Мусорка за домом",
    "База под мостом", "Крыша у Артёма", "Фонтан в парке", "Заброшенный пирс",
    "Старый пруд у школы", "Речка за гаражами", "Озеро в лесу", "Канал у завода",
    "Лиговский пруд", "Пулковский ручей", "Смоленка у кладбища", "Пруд у дач",
    "Река у вокзала", "Озеро в парке", "Пирс у реки", "Затон у порта"
]

# --- РЫБА ---
FISHES = [
    ("Окунь", "300 г"), ("Карась", "500 г"), ("Щука", "1.5 кг"),
    ("Лещ", "800 г"), ("Плотва", "200 г"), ("Сом", "3 кг"),
    ("Карп", "2.5 кг"), ("Судак", "1.2 кг"), ("Ерш", "150 г"),
    ("Голавль", "600 г"), ("Язь", "900 г"), ("Линь", "700 г"),
    ("Налим", "2 кг"), ("Жерех", "1.8 кг"), ("Форель", "1.1 кг"),
    ("Осетр", "5 кг"), ("Угорь", "1.5 кг"), ("Пескарь", "100 г"),
    ("Красноперка", "400 г"), ("Белоглазка", "350 г"), ("Толстолобик", "4 кг"),
    ("Белый амур", "3.5 кг"), ("Змееголов", "2.2 кг"), ("Ротан", "250 г"),
    ("Бычок", "120 г"), ("Колюшка", "50 г"), ("Вьюн", "80 г"),
    ("Горчак", "40 г"), ("Подуст", "550 г"), ("Рыбец", "450 г"),
    ("Шемая", "300 г"), ("Уклейка", "70 г"), ("Верховка", "30 г"),
    ("Быстрянка", "60 г"), ("Минога", "90 г"), ("Стерлядь", "2.8 кг")
]

# --- БОЛТАЛКА ---
TALK_RESPONSES = [
    "Интересно, расскажи ещё.", "А что было дальше?", "Жёстко, брат.",
    "Ну ты даёшь.", "Слушай, а что потом?", "Понял тебя.", "Это сильно.",
    "Давай подробнее.", "Хм, а почему так?", "Ого, вот это поворот.",
    "Ну нихрена себе.", "Я аж задумался.", "Слушай, а ты уверен?",
    "Вот это история.", "Мда, бывает.", "А я и не знал.",
    "Ты серьёзно?", "Круто, что ещё?", "Да ладно, не может быть.",
    "Продолжай, мне интересно.", "Хм, надо подумать.", "Согласен.",
    "Не, ну это пиздец, конечно.", "А я думал, ты шутишь.",
    "Охренеть.", "Забавно.", "Ну и ну.", "Вот так новости.",
    "Это меняет всё.", "Да, брат, дела.", "Уважаю.", "Сильно сказано.",
    "Мне нравится ход твоих мыслей.", "Хорошо, что сказал.",
    "Ага, понимаю.", "Слушай, а это мысль.", "Вот это да.",
    "Мощно.", "Ты меня удивил.", "Надо обмозговать.",
    "Интересный поворот.", "Понял, принял.", "А что дальше?",
    "Хм, звучит логично.", "Ну, допустим.", "Да ну, серьёзно?",
    "Вот это по-нашему.", "Красиво сказано.", "Мне заходит.",
    "А я думал иначе.", "Слушай, а ты прав.", "Ладно, убедил.",
    "Хорошая тема.", "Давай ещё.", "Я весь внимание.",
    "Ну ты и выдал.", "Вот это поворот сюжета.", "Слушай, а что если...",
    "Мне нравится, как ты мыслишь.", "Это по-настоящему мощно.",
    "Согласен на все сто.", "Вот это диалог.", "Да, есть над чем подумать.",
    "Ох, ну ты и загнул.", "Продолжай, не останавливайся.",
    "Вот это я понимаю.", "Сильно, брат, сильно.",
    "Аж мурашки по коже.", "Ты сегодня в ударе.",
    "Хм, а я и не подумал.", "Вот это новость.",
    "Да ладно, серьёзно?", "Ну, ты даёшь, конечно.",
    "Слушай, а это интересно.", "Вот это разговор пошёл.",
    "Мне нравится твой настрой.", "Уважение.",
    "Понял, брат.", "Давай, я слушаю.", "Хм, а что дальше?",
    "Вот это я понимаю, тема.", "Круто, что ещё скажешь?",
    "Слушай, а ты глубоко копаешь.", "Мощный заход.",
    "Ну, теперь всё ясно.", "Ага, вот так значит.",
    "Вот это по делу.", "Слушаю тебя внимательно.",
    "Интересно, а почему?", "Давай, развивай мысль."
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

# --- ФУНКЦИЯ "ДУМАНИЯ" ---
async def think_and_reply(update, text):
    await asyncio.sleep(random.uniform(0.5, 1.5))
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

# --- СТАРТ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Йо, Чувак! Выбирай:", reply_markup=get_main_keyboard())

# --- ОБРАБОТКА СООБЩЕНИЙ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_group = update.message.chat.type in ['group', 'supergroup']
    if is_group:
        bot_username = context.bot.username
        if f"@{bot_username}" not in update.message.text:
            return
    text = update.message.text.replace(f"@{context.bot.username}", "").strip()

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
        response = random.choice(TALK_RESPONSES)
        await think_and_reply(update, response)

# --- ВЕБ-СЕРВЕР ДЛЯ ПОРТА ---
def run_web_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def handle(request):
        return web.Response(text="Bot is running")

    app_web = web.Application()
    app_web.router.add_get('/', handle)
    runner = web.AppRunner(app_web)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    loop.run_until_complete(site.start())
    loop.run_forever()

# --- ЗАПУСК ---
if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
