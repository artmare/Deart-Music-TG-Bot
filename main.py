# --- Импорт и настройка ---
import asyncio
import logging
import os
import re
import tempfile
import subprocess
import requests
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
AUDD_API_TOKEN = getenv("AUDD_API_TOKEN")

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# --- Языковые шаблоны ---
LANGS = ["en", "ru"]
MESSAGES = {
    "en": {
        "start": "Hi! I can find music from video or TikTok.",
        "choose_lang": "Please select your language:",
        "main_menu": "Choose one of the options:",
        "find_music": "Find Music",
        "my_library": "My Library",
        "subscription": "Subscription",
        "profile": "Profile",
        "settings": "Settings",
        "send_video_or_link": "Send a video or TikTok link and I'll try to find the music 🎵",
        "processing": "⏳ Processing...",
        "not_tiktok": "Please send a valid TikTok link or video",
        "download_fail": "Failed to download TikTok video.",
        "extract_fail": "Failed to extract audio from video.",
        "recognize_fail": "Could not recognize music 😔 Try another video",
        "api_fail": "Recognition service error.",
        "found": "🎵 Found:\nTitle: {title}\nArtist: {artist}",
        "spotify": "\nSpotify: {url}",
        "apple": "\nApple Music: {url}",
        "error": "An error occurred."
    },
    "ru": {
        "start": "<b>Добро пожаловать в Deart Music bot!</b> <tg-emoji emoji-id=\"5273993279963156863\">🎧</tg-emoji>\n\nНаш бот помогает мгновенно находить почти любые треки и исполнителей со всего мира. Больше не нужно тратить время на долгий поиск — просто введите название, и результат появится за считанные секунды.\n\nВы можете слушать музыку онлайн прямо в боте или скачивать её в высоком качестве всего за пару кликов. Всё максимально просто, удобно и без лишних действий.\n\n<tg-emoji emoji-id=\"5190694914698000117\">🔤</tg-emoji> <tg-emoji emoji-id=\"5193205026729769406\">🔤</tg-emoji>\nМы постоянно улучшаем функционал и добавляем новые возможности, чтобы сделать использование ещё быстрее и комфортнее. Удобный интерфейс, стабильная работа и высокая скорость — наши главные приоритеты.\n\n(А также в описание бота вы сможете найти людей которые создали этот бот, если у вас появиться проблема или вы захотите что то в него добавить вы можете сообщить нам в лс!)\n\nМы ценим простоту, стиль и качество, чтобы вы могли полностью погрузиться в музыку и наслаждаться любимыми треками в любое время.\n\nПросто напишите название песни и начните слушать уже сейчас <tg-emoji emoji-id=\"5231101979903675433\">✨</tg-emoji>",
        "choose_lang": "Пожалуйста, выберите язык:",
        "main_menu": "Выберите один из вариантов:",
        "find_music": "Найти музыку",
        "my_library": "Моя Медиатека",
        "subscription": "Подписка",
        "profile": "Профиль",
        "settings": "Настройки",
        "send_video_or_link": "Отправь видео или ссылку на TikTok, и я попробую найти музыку 🎵",
        "processing": "⏳ Обрабатываю...",
        "not_tiktok": "Пожалуйста, отправь корректную ссылку TikTok или видео",
        "download_fail": "Не удалось скачать видео с TikTok.",
        "extract_fail": "Не удалось извлечь аудио из видео.",
        "recognize_fail": "Не удалось определить музыку 😔 Попробуй другое видео",
        "api_fail": "Ошибка сервиса распознавания.",
        "found": "🎵 Найдено:\nНазвание: {title}\nИсполнитель: {artist}",
        "spotify": "\nSpotify: {url}",
        "apple": "\nApple Music: {url}",
        "error": "Произошла ошибка.",
        "start": """
            
        Добро пожаловать в Deart Music bot! \n\n
        Наш бот помогает мгновенно находить почти любые треки и исполнителей со всего мира. Больше не нужно тратить время на долгий поиск — просто введите название, и результат появится за считанные секунды.\n\n
        Вы можете слушать музыку онлайн прямо в боте или скачивать её в высоком качестве всего за пару кликов. Всё максимально просто, удобно и без лишних действий.\n\n
        \n
        Мы постоянно улучшаем функционал и добавляем новые возможности, чтобы сделать использование ещё быстрее и комфортнее. Удобный интерфейс, стабильная работа и высокая скорость — наши главные приоритеты.\n\n
        (А также в описание бота вы сможете найти людей которые создали этот бот, если у вас появиться проблема или вы захотите что то в него добавить вы можете сообщить нам в лс!)\n\n
        Мы ценим простоту, стиль и качество, чтобы вы могли полностью погрузиться в музыку и наслаждаться любимыми треками в любое время.\n\n
        Просто напишите название песни и начните слушать уже сейчас 
        
    """
    }
}

# --- Клавиатуры ---
def get_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="English", callback_data="lang_en")],
            [InlineKeyboardButton(text="Русский", callback_data="lang_ru")]
        ]
    )

def get_main_menu_keyboard(lang="ru"):
    m = MESSAGES[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=m["find_music"], callback_data=f"find_music_{lang}")],
            [InlineKeyboardButton(text=m["my_library"], callback_data=f"my_library_{lang}")],
            [InlineKeyboardButton(text=m["subscription"], callback_data=f"subscription_{lang}")],
            [InlineKeyboardButton(text=m["profile"], callback_data=f"profile_{lang}")],
            [InlineKeyboardButton(text=m["settings"], callback_data=f"settings_{lang}")],
        ]
    )

# --- Хранилище выбора языка (in-memory, для примера) ---
user_lang = {}

def get_user_lang(user_id):
    return user_lang.get(user_id, "ru")

def set_user_lang(user_id, lang):
    if lang in LANGS:
        user_lang[user_id] = lang

# --- Хендлеры ---
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(MESSAGES["ru"]["start"], parse_mode="HTML")
    await message.answer(MESSAGES["ru"]["choose_lang"], reply_markup=get_language_keyboard())

@dp.callback_query(F.data.in_(["lang_en", "lang_ru"]))
async def language_select_handler(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    set_user_lang(callback.from_user.id, lang)
    await callback.message.answer(MESSAGES[lang]["main_menu"], reply_markup=get_main_menu_keyboard(lang))
    await callback.answer()

@dp.callback_query(F.data.regexp(r"find_music_(en|ru)"))
async def find_music_handler(callback: CallbackQuery):
    lang = callback.data.split("_")[-1]
    set_user_lang(callback.from_user.id, lang)
    await callback.message.answer(MESSAGES[lang]["send_video_or_link"])
    await callback.answer()

# --- Обработчик подписки ---
@dp.callback_query(F.data.regexp(r"subscription_(en|ru)"))
async def subscription_handler(callback: CallbackQuery):
    lang = callback.data.split("_")[-1]
    set_user_lang(callback.from_user.id, lang)
    # Здесь можно добавить логику проверки подписки пользователя через database.py
    from database import get_subscription
    user_id = callback.from_user.id
    sub_type, sub_end = get_subscription(user_id)
    if sub_type and sub_end:
        text = f"\U0001F4B3 {MESSAGES[lang]['subscription']}\nТип: {sub_type}\nДействует до: {sub_end}"
        await callback.message.answer(text)
    else:
        text = f"\U0001F4B3 {MESSAGES[lang]['subscription']}\nНет активной подписки."
        await callback.message.answer(text)
        # Сообщение с выбором тарифа
        choose_text = "Выбери подписку:" if lang == "ru" else "Choose a subscription:"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1 месяц — 199₽", callback_data="buy_sub_1m")],
                [InlineKeyboardButton(text="3 месяца — 499₽", callback_data="buy_sub_3m")],
                [InlineKeyboardButton(text="12 месяцев — 1490₽", callback_data="buy_sub_12m")],
            ]
        )
        await callback.message.answer(choose_text, reply_markup=keyboard)
    await callback.answer()

# --- Обработчик покупки подписки ---
@dp.callback_query(F.data.in_(["buy_sub_1m", "buy_sub_3m", "buy_sub_12m"]))
async def buy_subscription_handler(callback: CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    tariff_map = {
        "buy_sub_1m": ("1 месяц", "199₽", "1 month", "199₽"),
        "buy_sub_3m": ("3 месяца", "499₽", "3 months", "499₽"),
        "buy_sub_12m": ("12 месяцев", "1490₽", "12 months", "1490₽"),
    }
    t = tariff_map[callback.data]
    if lang == "ru":
        text = f"Вы выбрали тариф: {t[0]} — {t[1]}\n\nОплата пока не реализована. Свяжитесь с поддержкой для оформления подписки."
    else:
        text = f"You selected: {t[2]} — {t[3]}\n\nPayment is not implemented yet. Please contact support to activate your subscription."
    await callback.message.answer(text)
    await callback.answer()

@dp.message(F.text)
async def handle_text(message: Message):
    lang = get_user_lang(message.from_user.id)
    text = message.text.strip()
    if is_tiktok_url(text):
        await message.answer(MESSAGES[lang]["processing"])
        await process_tiktok_link(message, text, lang)
    else:
        await message.answer(MESSAGES[lang]["not_tiktok"])

@dp.message(F.video)
async def handle_video(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(MESSAGES[lang]["processing"])
    await process_video_file(message, lang)

# --- Вспомогательные функции ---
def is_tiktok_url(url: str) -> bool:
    # Поддержка обычных и коротких ссылок TikTok
    return (
        re.match(r'https?://(www\.)?tiktok\.com/', url) is not None or
        re.match(r'https?://vm\.tiktok\.com/', url) is not None
    )

async def process_tiktok_link(message: Message, url: str, lang: str):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            result = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "-o", video_path, url],
                capture_output=True, text=True
            )
            if result.returncode != 0 or not os.path.exists(video_path):
                await message.answer(MESSAGES[lang]["download_fail"])
                logging.error(result.stderr)
                return
            await extract_and_recognize_audio(message, video_path, lang)
    except Exception as e:
        logging.exception("Ошибка при обработке TikTok ссылки")
        await message.answer(MESSAGES[lang]["error"])

async def process_video_file(message: Message, lang: str):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "video.mp4")
            await message.video.download(destination=video_path)
            await extract_and_recognize_audio(message, video_path, lang)
    except Exception as e:
        logging.exception("Ошибка при обработке видео")
        await message.answer(MESSAGES[lang]["error"])

async def extract_and_recognize_audio(message: Message, video_path: str, lang: str):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "audio.mp3")
            result = subprocess.run(
                ["ffmpeg", "-i", video_path, "-vn", "-acodec", "mp3", "-y", audio_path],
                capture_output=True, text=True
            )
            if result.returncode != 0 or not os.path.exists(audio_path):
                await message.answer(MESSAGES[lang]["extract_fail"])
                logging.error(result.stderr)
                return
            await recognize_music(message, audio_path, lang)
    except Exception as e:
        logging.exception("Ошибка при извлечении аудио")
        await message.answer(MESSAGES[lang]["error"])

async def recognize_music(message: Message, audio_path: str, lang: str):
    try:
        with open(audio_path, "rb") as f:
            files = {"file": f}
            data = {"api_token": AUDD_API_TOKEN, "return": "spotify,apple_music"}
            response = requests.post("https://api.audd.io/", data=data, files=files)
        if response.status_code != 200:
            await message.answer(MESSAGES[lang]["api_fail"])
            return
        result = response.json()
        if result.get("status") != "success" or not result.get("result"):
            await message.answer(MESSAGES[lang]["recognize_fail"])
            return
        track = result["result"]
        msg = MESSAGES[lang]["found"].format(title=track.get("title"), artist=track.get("artist"))
        if track.get("spotify") and track["spotify"].get("external_urls"):
            msg += MESSAGES[lang]["spotify"].format(url=track["spotify"]["external_urls"].get("spotify"))
        if track.get("apple_music") and track["apple_music"].get("url"):
            msg += MESSAGES[lang]["apple"].format(url=track["apple_music"]["url"])
        await message.answer(msg)
    except Exception as e:
        logging.exception("Ошибка при распознавании музыки")
        await message.answer(MESSAGES[lang]["error"])

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Инициализация базы данных
    from database import init_db
    init_db()
    asyncio.run(main())

