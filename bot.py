import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ================= НАСТРОЙКИ =================

TOKEN = "8090223138:AAHn1CfZz9ZEunoJ5GLK905DWitKbgm5rv0"
CHAT_ID = -1003887800683  # ID группы / супергруппы

TEXT = "Здравствуйте, коллеги, напоминаю, что сегодня по расписанию пересчёт!"

# =============================================

logging.basicConfig(level=logging.INFO)

bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))

# Храним кто нажал кнопку (message_id -> set(user_id))
acknowledged = {}


# ---------- КНОПКА ----------
def get_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Уведомление было прочитано",
                callback_data="ack"
            )]
        ]
    )


# ---------- ОТПРАВКА УВЕДОМЛЕНИЯ ----------
async def send_notice(label: str):
    msg = await bot.send_message(
        chat_id=CHAT_ID,
        text=f"<b>{TEXT}</b>\n\n<i>{label}</i>",
        reply_markup=get_keyboard()
    )
    acknowledged[msg.message_id] = set()


# ---------- ОБРАБОТКА КНОПКИ ----------
@dp.callback_query(F.data == "ack")
async def ack_handler(call: CallbackQuery):
    msg_id = call.message.message_id
    user_id = call.from_user.id

    users = acknowledged.setdefault(msg_id, set())
    users.add(user_id)

    text = f"<b>{TEXT}</b>\n\n<b>Ознакомились:</b>\n"
    for uid in users:
        text += f"• <code>{uid}</code>\n"

    await call.message.edit_text(text, reply_markup=get_keyboard())
    await call.answer("Отмечено ✅")


# ---------- КОМАНДА /test ----------
@dp.message(Command("test"))
async def test_command(message: Message):
    await send_notice("🧪 ТЕСТОВОЕ УВЕДОМЛЕНИЕ")


# ---------- ПЛАНИРОВЩИК ----------
def setup_scheduler():
    scheduler.add_job(
        send_notice,
        trigger="cron",
        hour=4,
        minute=0,
        args=["🌙 Ночная смена (04:00)"]
    )

    scheduler.add_job(
        send_notice,
        trigger="cron",
        hour=10,
        minute=0,
        args=["☀️ Дневная смена (10:00)"]
    )

    scheduler.start()


# ---------- ЗАПУСК ----------
async def main():
    setup_scheduler()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
