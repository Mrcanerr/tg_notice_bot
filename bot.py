import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

# ================= НАСТРОЙКИ =================
TOKEN = os.getenv("BOT_TOKEN") or "8090223138:AAHn1CfZz9ZEunoJ5GLK905DWitKbgm5rv0"
CHAT_ID = -5221691294  # ID группы
# ============================================

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

read_users = {}
current_shift = ""

# ---------- КНОПКА ----------
def keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Уведомление было прочитано",
                    callback_data="read_notice"
                )
            ]
        ]
    )

# ---------- ТЕКСТ СООБЩЕНИЯ ----------
def build_text():
    text = (
        "Здравствуйте, коллеги, напоминаю, что сегодня по расписанию пересчет!\n\n"
        f"<b>Смена:</b> {current_shift}\n"
    )

    if read_users:
        text += "\n<b>Прочитали:</b>\n"
        for uid, username in read_users.items():
            name = f"@{username}" if username else "без username"
            text += f"• {name} (<code>{uid}</code>)\n"

    return text

# ---------- ОТПРАВКА УВЕДОМЛЕНИЯ ----------
async def send_notice(shift_name: str):
    global read_users, current_shift
    read_users = {}
    current_shift = shift_name

    await bot.send_message(
        chat_id=CHAT_ID,
        text=build_text(),
        reply_markup=keyboard()
    )

# ---------- НАЖАТИЕ КНОПКИ ----------
@dp.callback_query(F.data == "read_notice")
async def read_callback(call: CallbackQuery):
    user = call.from_user

    if user.id not in read_users:
        read_users[user.id] = user.username
        await call.message.edit_text(
            build_text(),
            reply_markup=keyboard()
        )

    await call.answer("Отмечено 👍")

# ---------- КОМАНДА /test ----------
@dp.message(Command("test"))
async def test_command(message):
    await send_notice("ТЕСТОВАЯ СМЕНА")

# ---------- ЗАПУСК ----------
async def main():
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))

    scheduler.add_job(send_notice, "cron", hour=4, minute=0, args=["Ночная (04:00)"])
    scheduler.add_job(send_notice, "cron", hour=10, minute=0, args=["Дневная (10:00)"])

    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
