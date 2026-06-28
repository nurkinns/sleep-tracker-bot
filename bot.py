from database import add_user, save_sleep_start, save_sleep_end, get_user_stats, set_user_language, get_user_language, delete_user_stats
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

TRANSLATIONS = {
    "EN": {
        "sleep_btn": "🛏️ Sleep", 
        "awake_btn": "☀️ Awake", 
        "stats_btn": "💾 Statistics", 
        "settings_btn": "⚙️ Settings",
        "see_ya": "See ya!",
        "morning": "Morning!",
        "reset_btn": "🗑️ Reset Stats",
        "reset_done": "All sleep records has been deleted successfully!",
        "back_btn": "⬅️ Back",
        "settings_title": "Settings / Настройки:",
        "stats_title": "📊 YOUR SLEEP STATISTICS",
        "stats_empty": "🤷‍♂️ You don't have any sleep records yet. Click 'Sleep' to start tracking!",
        "stats_line": "Sleep time",
        "hours_letter": "h",
        "minutes_letter": "m"
    },
    "RU": {
        "sleep_btn": "🛏️ Уснуть", 
        "awake_btn": "☀️ Проснуться", 
        "stats_btn": "💾 Статистика", 
        "settings_btn": "⚙️ Настройки",
        "see_ya": "Увидимся!",
        "morning": "Утро доброе!",
        "reset_btn": "🗑️ Сбросить статистику",
        "reset_done": "Все записи о сне успешно удалены!",
        "back_btn": "⬅️ Назад",
        "settings_title": "Настройки / Settings:",
        "stats_title": "📊 ВАША СТАТИСТИКА СНА",
        "stats_empty": "🤷‍♂️ У вас пока нет записей о сне. Нажмите «Уснуть», чтобы начать трекинг!",
        "stats_line": "Время сна",
        "hours_letter": "ч",
        "minutes_letter": "м"
    }
}

def get_keyboard(state, user_id):
    lang = get_user_language(user_id)
    buttons = TRANSLATIONS[lang]

    main_text = buttons["sleep_btn"] if state == "sleep" else buttons["awake_btn"]
    
    main_button = KeyboardButton(text=main_text)
    stats_button = KeyboardButton(text=buttons["stats_btn"])
    settings_button = KeyboardButton(text=buttons["settings_btn"])

    return ReplyKeyboardMarkup(
        keyboard=[[main_button], [stats_button, settings_button]], 
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start_handler(message: Message):
    add_user(message.from_user.id)
    await message.answer(
        "Hi! Im - Bot for tracking your awake time, bedtime and sleep duration",
        reply_markup=get_keyboard("sleep", message.from_user.id)
    )

@dp.message((F.text == "🛏️ Sleep") | (F.text == "🛏️ Уснуть"))
async def sleep_handler(message: Message):
    save_sleep_start(message.from_user.id)
    lang = get_user_language(message.from_user.id)
    
    await message.answer(
        TRANSLATIONS[lang]["see_ya"],
        reply_markup=get_keyboard("awake", message.from_user.id)
    )

@dp.message((F.text == "☀️ Awake") | (F.text == "☀️ Проснуться"))
async def awake_handler(message: Message):
    save_sleep_end(message.from_user.id)
    lang = get_user_language(message.from_user.id)
    
    await message.answer(
        TRANSLATIONS[lang]["morning"],
        reply_markup=get_keyboard("sleep", message.from_user.id)
    )

@dp.message((F.text == "💾 Statistics") | (F.text == "💾 Статистика"))
async def stats_handler(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    buttons = TRANSLATIONS[lang]
    
    records = get_user_stats(user_id)
    
    if not records:
        await message.answer(buttons["stats_empty"])
        return

    response_text = f"<b>{buttons['stats_title']}</b>\n"
    response_text += "━━━━━━━━━━━━━━━━━━━━━\n"
    
    for date_display, start_display, end_display, hours, minutes in records:
        h_let = buttons["hours_letter"]
        m_let = buttons["minutes_letter"]
        lbl = buttons["stats_line"]
        
        response_text += (
            f"📅 <b>{date_display}</b>\n"
            f"🌙 {start_display} — ☀️ {end_display}\n"
            f"✨ {lbl}: <code>{hours}{h_let} {minutes}{m_let}</code>\n"
            f"─────────────────────\n"
        )
        
    response_text += "━━━━━━━━━━━━━━━━━━━━━"
    await message.answer(response_text, parse_mode="HTML")

@dp.message((F.text == "⚙️ Settings") | (F.text == "⚙️ Настройки"))
async def settings_handler(message: Message):
    lang = get_user_language(message.from_user.id)
    buttons = TRANSLATIONS[lang]

    en_btn = KeyboardButton(text="🇬🇧 EN")
    ru_btn = KeyboardButton(text="🇷🇺 RU")
    del_btn = KeyboardButton(text=buttons["reset_btn"])
    back_btn = KeyboardButton(text=buttons["back_btn"])

    lang_keyboard = ReplyKeyboardMarkup(
        keyboard=[[en_btn, ru_btn], [del_btn], [back_btn]],
        resize_keyboard=True
    )
    await message.answer(buttons["settings_title"], reply_markup=lang_keyboard)

@dp.message(F.text == "🇬🇧 EN")
async def lang_en_handler(message: Message):
    set_user_language(message.from_user.id, "EN")
    await message.answer("Language changed to English!", reply_markup=get_keyboard("sleep", message.from_user.id))

@dp.message(F.text == "🇷🇺 RU")
async def lang_ru_handler(message: Message):
    set_user_language(message.from_user.id, "RU")
    await message.answer("Язык изменен на русский!", reply_markup=get_keyboard("sleep", message.from_user.id))

@dp.message((F.text == "⬅️ Back") | (F.text == "⬅️ Назад"))
async def back_handler(message: Message):
    await message.answer("Main menu / Главное меню", reply_markup=get_keyboard("sleep", message.from_user.id))

@dp.message((F.text == "🗑️ Reset Stats") | (F.text == "🗑️ Сбросить статистику"))
async def delete_stats_handler(message: Message):
    delete_user_stats(message.from_user.id)
    lang = get_user_language(message.from_user.id)
    await message.answer(TRANSLATIONS[lang]["reset_done"], reply_markup=get_keyboard("sleep", message.from_user.id))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

#made by "nurkinns" on GitHub with using AI.