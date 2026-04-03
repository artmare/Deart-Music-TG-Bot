from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from subscriptions import TARIFFS, check_subscription, activate_subscription
from payments import generate_payment_link, check_payment

router = Router()

def get_subscription_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подписка на неделю — 2€", callback_data="tariff_week")],
            [InlineKeyboardButton(text="Подписка на месяц — 5€", callback_data="tariff_month")],
            [InlineKeyboardButton(text="Подписка на полгода — 25€", callback_data="tariff_6months")],
            [InlineKeyboardButton(text="Подписка на год — 40€", callback_data="tariff_year")],
        ]
    )

@router.message(F.text == "Подписка")
async def subscription_menu(message: Message):
    await message.answer("Выберите подходящий тариф 💎", reply_markup=get_subscription_menu())

@router.callback_query(F.data.startswith("tariff_"))
async def process_tariff(callback: CallbackQuery):
    tariff = callback.data.split("_")[1]
    await callback.answer()
    await callback.message.answer("⏳ Генерирую ссылку для оплаты...")
    link = generate_payment_link(callback.from_user.id, tariff)
    await callback.message.answer(f"💳 Оплатите подписку по ссылке:\n{link}")

    # В реальном проекте: после оплаты вызвать activate_subscription()
    # Здесь — имитация успешной оплаты:
    activate_subscription(callback.from_user.id, tariff)
    await callback.message.answer("✅ Подписка активирована!")

@router.message(F.text == "Музыка")
async def music_feature(message: Message):
    if not check_subscription(message.from_user.id):
        await message.answer("❌ Эта функция доступна только по подписке")
    else:
        await message.answer("🎵 Поиск музыки доступен!")
