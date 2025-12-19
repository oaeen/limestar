"""Telegram Bot - 主入口和启动逻辑"""

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config import settings
from app.bot.handlers import (
    start,
    help_cmd,
    list_links,
    search_links,
    handle_message,
)


def create_bot() -> Application:
    """创建并配置 Bot 应用"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN 未配置")

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # 注册命令处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("list", list_links))
    app.add_handler(CommandHandler("search", search_links))

    # 注册消息处理器（处理链接）
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    return app


def run_polling():
    """以 Polling 模式运行 Bot（阻塞）"""
    print("LimeStar Telegram Bot 启动中...")

    app = create_bot()

    # 显示白名单信息
    allowed = settings.get_allowed_users()
    if allowed:
        print(f"白名单模式已启用，允许的用户 ID: {allowed}")
    else:
        print("警告: 未配置白名单，任何人都可以使用此 Bot")

    print("Bot 已启动，按 Ctrl+C 停止")

    # 启动 polling
    app.run_polling(
        allowed_updates=["message"],
        drop_pending_updates=True,  # 忽略离线期间的消息
    )
