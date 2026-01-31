import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = -1001234567890  # ID группы

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

read_users = {}  # user_id: username
current_shift = ""

def keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Уведомление было прочитано",
                callback_data="read"
            )]
        ]
    )

def build_text():
    text = (
        "Здравствуйте, коллеги, напоминаю, что сегодня по расписанию пересчет!\n\n"
        f"<b>Смена:</b> {current_shift}\n"
    )

    if read_users:
        text += "\n<b>Прочитали:</b>\n"
        for uid, uname in read_users.items():
            name = f"@{uname}" if uname else "без username"
            text += f"• {name} (<code>{uid}</code>)\n"

    return text

async def send_notice(shift_name):
    global read_users, current_shift
    read_users = {}
    current_shift = shift_name

    await bot.send_message(
        chat_id=CHAT_ID,
        text=build_text(),
        reply_markup=keyboard()
    )

@dp.callback_query(F.data == "read")
async def read_callback(call: CallbackQuery):
    user = call.from_user

    if user.id not in read_users:
        read_users[user.id] = user.username
        await call.message.edit_text(
            build_text(),
            reply_markup=keyboard()
        )

    await call.answer("Отметка принята")

async def main():
    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))

    scheduler.add_job(send_notice, "cron", hour=4, minute=0, args=["Ночная (04:00)"])
    scheduler.add_job(send_notice, "cron", hour=10, minute=0, args=["Дневная (10:00)"])

    scheduler.start()
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
