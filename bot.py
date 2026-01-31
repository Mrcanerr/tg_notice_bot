import asyncio
import logging
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "8090223138:AAHn1CfZz9ZEunoJ5GLK905DWitKbgm5rv0"
CHAT_ID = -1003887800683  # ID группы

TEXT = "Здравствуйте, коллеги, напоминаю, что сегодня по расписанию пересчет!"

logging.basicConfig(level=logging.INFO)

bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
read_users = {}

def keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Уведомление было прочитано",
                callback_data="read"
            )]
        ]
    )

def build_text(msg_id: int):
    text = f"<b>{TEXT}</b>\n\n<b>Прочитали:</b>\n"
    for uid in read_users.get(msg_id, set()):
        text += f"• <code>{uid}</code>\n"
    return text

async def send_notice(label: str):
    msg = await bot.send_message(
        CHAT_ID,
        f"<b>{TEXT}</b>\n\n<i>{label}</i>",
        reply_markup=keyboard()
    )
    read_users[msg.message_id] = set()

@dp.callback_query(F.data == "read")
async def mark_read(call: CallbackQuery):
    mid = call.message.message_id
    uid = call.from_user.id

    read_users.setdefault(mid, set()).add(uid)

    await call.message.edit_text(
        build_text(mid),
        reply_markup=keyboard()
    )
    await call.answer("Отмечено 👍")

@dp.message(Command("test"))
async def test_command(message: Message):
    await send_notice("🧪 ТЕСТ")

def setup_jobs():
    scheduler.add_job(send_notice, "cron", hour=4, minute=0, args=["🌙 Ночная смена"])
    scheduler.add_job(send_notice, "cron", hour=10, minute=0, args=["☀️ Дневная смена"])
    scheduler.start()

async def main():
    setup_jobs()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
