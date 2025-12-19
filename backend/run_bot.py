#!/usr/bin/env python3
"""LimeStar Telegram Bot 启动脚本"""

import sys
from pathlib import Path

# 确保可以导入 app 模块
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db
from app.bot.telegram_bot import run_polling


def main():
    """主入口"""
    # 初始化数据库
    init_db()

    # 启动 Bot
    run_polling()


if __name__ == "__main__":
    main()
