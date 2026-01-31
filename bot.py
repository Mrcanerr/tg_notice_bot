import asyncio
import logging
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ============= НАСТРОЙКИ =============
TOKEN = "ВАШ_BOT_TOKEN"
CHAT_ID = -1001234567890  # ID вашей группы

NOTICE_TEXT = (
    "Здравствуйте, коллеги, напоминаю, что сегодня по расписанию пересчет!"
)

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Планировщик
scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))

read_users = {}  # message_id -> set(user_id)

def build_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Уведомление было прочитано", callback_data="ack")]
        ]
    )

def build_text(msg_id: int):
    text = NOTICE_TEXT + "\n\n<b>Прочитали:</b>\n"
    for uid in read_users.get(msg_id, set()):
        text += f"• <code>{uid}</code>\n"
    return text

async def send_notice(label: str):
    message = await bot.send_message(
        chat_id=CHAT_ID,
        text=f"<b>{NOTICE_TEXT}</b>\n\n<i>{label}</i>",
        reply_markup=build_keyboard()
    )
    read_users[message.message_id] = set()

@dp.callback_query(F.data == "ack")
async def handle_ack(call: CallbackQuery):
    msg_id = call.message.message_id
    user_id = call.from_user.id

    read_users.setdefault(msg_id, set()).add(user_id)

    await call.message.edit_text(
        build_text(msg_id),
        reply_markup=build_keyboard()
    )

    await call.answer("Отмечено 👌")

@dp.message(Command("test"))
async def cmd_test(message: Message):
    await send_notice("🧪 ТЕСТОВОЕ УВЕДОМЛЕНИЕ")

def setup_scheduler():
    scheduler.add_job(send_notice, "cron", hour=4, minute=0, args=["🌙 Ночная (04:00)"])
    scheduler.add_job(send_notice, "cron", hour=10, minute=0, args=["☀️ Дневная (10:00)"])
    scheduler.start()

async def main():
    setup_scheduler()
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
