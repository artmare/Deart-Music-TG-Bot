
import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


# Function to return the language selection keyboard
def get_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="English", callback_data="language_en")],
            [InlineKeyboardButton(text="Russian", callback_data="language_ru")]
        ]
    )

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Hi, It is Deart Music Bot!")
    await message.answer("Please select your language:", reply_markup=get_language_keyboard())


# Handler for language selection (message)
@dp.message()
async def language_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="English", callback_data="language_en")],
            [InlineKeyboardButton(text="Russian", callback_data="language_ru")]
        ]
    )
    await message.answer("Please select your language:", reply_markup=keyboard)

# Handler for button clicks (callback query)
from aiogram.types import CallbackQuery
from aiogram import F

@dp.callback_query(F.data.in_(["language_en", "language_ru"]))
async def language_callback_handler(callback: CallbackQuery):
    if callback.data == "language_en":
        await callback.message.answer("You selected English.")
    elif callback.data == "language_ru":
        await callback.message.answer("Вы выбрали русский язык.")
    await callback.answer()

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    