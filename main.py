import asyncio
import logging
import sys

# Fix Python 3.12.0 typing.Union hash compatibility with Pydantic FailFast
try:
    from pydantic import FailFast
    if not hasattr(FailFast, "__hash__") or FailFast.__hash__ is None:
        FailFast.__hash__ = lambda self: hash(getattr(self, "fail_fast", True))
except Exception:
    pass

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, ADMIN_ID
from database import init_db
from handlers import start, order, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="বট শুরু করুন ও মেনু দেখুন"),
        BotCommand(command="order", description="সরাসরি প্রোডাক্ট অর্ডার করুন"),
        BotCommand(command="product", description="প্রোডাক্টের বিবরণ ও মূল্য তালিকা"),
        BotCommand(command="myorder", description="আপনার অর্ডারের বর্তমান অবস্থা"),
        BotCommand(command="help", description="হেল্প ও কাস্টমার সাপোর্ট"),
    ]
    await bot.set_my_commands(commands)

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logger.error(
            "\n"
            "==========================================================\n"
            "❌ ERROR: BOT_TOKEN is missing or not set in .env file!\n"
            "অনুগ্রহ করে .env ফাইলটি ওপেন করে আপনার BOT_TOKEN দিন।\n"
            "যেমন: BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ\n"
            "==========================================================\n"
        )
        sys.exit(1)

    logger.info("Initializing database...")
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(order.router)

    # Set commands in Telegram
    try:
        await set_bot_commands(bot)
        logger.info("Bot commands registered successfully.")
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")

    me = await bot.get_me()
    logger.info(f"Bot started successfully as @{me.username} ({me.first_name})")
    if ADMIN_ID and ADMIN_ID != 0:
        logger.info(f"Admin notifications active for Telegram ID: {ADMIN_ID}")
    else:
        logger.warning("ADMIN_ID not configured in .env! Admin alerts won't be sent.")

    # Drop pending updates and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        from database import close_pg_pool
        await close_pg_pool()
        await bot.session.close()
        logger.info("Bot stopped.")
