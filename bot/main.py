#!/usr/bin/env python3
"""
Entry point — starts the Telegram bot in polling mode.
"""
import asyncio
import logging
import sys
from bot.handlers import build_application, set_bot_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def main() -> None:
    app = build_application()
    await set_bot_commands(app)

    logger.info("🤖 Assistant Telegram démarré — en attente de messages...")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
