#!/usr/bin/env python3
"""
LimeStar CLI - Command line tool for adding links locally.

Usage:
    python cli.py add <url> [--note "your note"]
    python cli.py list
    python cli.py search <keyword>
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine, init_db
from app.models import Link, Tag
from app.services.link_processor import link_processor


def print_link(link: Link) -> None:
    """Pretty print a link"""
    tags_str = ", ".join([t.name for t in link.tags]) if link.tags else "无标签"
    status = "✓" if link.is_processed else "..."

    print(f"\n[{status}] {link.title}")
    print(f"    URL: {link.url}")
    print(f"    描述: {link.description[:100]}..." if len(link.description) > 100 else f"    描述: {link.description}")
    print(f"    标签: {tags_str}")
    print(f"    时间: {link.created_at.strftime('%Y-%m-%d %H:%M')}")


async def add_link(url: str, note: str = None) -> None:
    """Add and process a new link"""
    print(f"\n正在处理: {url}")
    if note:
        print(f"备注: {note}")

    with Session(engine) as session:
        try:
            link = await link_processor.add_and_process_link(
                url=url,
                user_note=note,
                session=session,
                submitted_by="cli",
            )
            print("\n✓ 处理完成!")
            print_link(link)

        except Exception as e:
            print(f"\n✗ 处理失败: {e}")
            raise


def list_links(limit: int = 20) -> None:
    """List recent links"""
    with Session(engine) as session:
        links = session.exec(
            select(Link).order_by(Link.created_at.desc()).limit(limit)
        ).all()

        if not links:
            print("\n暂无收藏的链接")
            return

        print(f"\n最近 {len(links)} 条链接:")
        for link in links:
            print_link(link)


def search_links(keyword: str) -> None:
    """Search links by keyword"""
    with Session(engine) as session:
        search_term = f"%{keyword}%"
        links = session.exec(
            select(Link).where(
                (Link.title.ilike(search_term)) |
                (Link.description.ilike(search_term)) |
                (Link.user_note.ilike(search_term))
            ).order_by(Link.created_at.desc())
        ).all()

        if not links:
            print(f"\n未找到包含 '{keyword}' 的链接")
            return

        print(f"\n找到 {len(links)} 条匹配的链接:")
        for link in links:
            print_link(link)


def list_tags() -> None:
    """List all tags"""
    with Session(engine) as session:
        tags = session.exec(select(Tag)).all()

        if not tags:
            print("\n暂无标签")
            return

        print(f"\n共 {len(tags)} 个标签:")
        for tag in tags:
            count = len(tag.links)
            print(f"  • {tag.name} ({count})")


def interactive_mode():
    """交互式对话模式"""
    print("\n🍋 LimeStar 链接收藏助手")
    print("=" * 40)
    print("命令说明:")
    print("  • 直接输入 URL 添加链接")
    print("  • 输入 URL + 空格 + 备注 可附加说明")
    print("  • list    - 查看最近的链接")
    print("  • search <关键词> - 搜索链接")
    print("  • tags    - 查看所有标签")
    print("  • help    - 显示帮助")
    print("  • quit/exit/q - 退出")
    print("=" * 40)

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            # 退出命令
            if user_input.lower() in ("quit", "exit", "q"):
                print("👋 再见!")
                break

            # 帮助命令
            if user_input.lower() == "help":
                print("\n命令说明:")
                print("  • 直接输入 URL 添加链接")
                print("  • 输入 URL + 空格 + 备注 可附加说明")
                print("  • list    - 查看最近的链接")
                print("  • search <关键词> - 搜索链接")
                print("  • tags    - 查看所有标签")
                print("  • quit/exit/q - 退出")
                continue

            # list 命令
            if user_input.lower() == "list":
                list_links()
                continue

            # tags 命令
            if user_input.lower() == "tags":
                list_tags()
                continue

            # search 命令
            if user_input.lower().startswith("search "):
                keyword = user_input[7:].strip()
                if keyword:
                    search_links(keyword)
                else:
                    print("请输入搜索关键词，如: search AI")
                continue

            # 添加链接 - 检测是否是 URL（支持不带协议前缀的域名）
            # 解析 URL 和备注
            parts = user_input.split(maxsplit=1)
            potential_url = parts[0]

            # 判断是否像一个URL（包含点号且不是纯命令）
            if "." in potential_url and not potential_url.startswith("."):
                url = potential_url
                # 添加 https:// 前缀（如果没有）
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                note = parts[1] if len(parts) > 1 else None

                asyncio.run(add_link(url, note))
            else:
                print(f"未识别的命令: {user_input}")
                print("提示: 输入 help 查看帮助，或直接输入 URL 添加链接")

        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except EOFError:
            print("\n👋 再见!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="LimeStar CLI - 链接收藏命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py                                  # 进入交互式模式
  python cli.py add https://example.com
  python cli.py add https://example.com --note "这是一个很棒的网站"
  python cli.py list
  python cli.py search AI
  python cli.py tags
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # add command
    add_parser = subparsers.add_parser("add", help="添加新链接")
    add_parser.add_argument("url", help="要添加的 URL")
    add_parser.add_argument("--note", "-n", help="附加备注")

    # list command
    list_parser = subparsers.add_parser("list", help="列出最近的链接")
    list_parser.add_argument("--limit", "-l", type=int, default=20, help="显示数量")

    # search command
    search_parser = subparsers.add_parser("search", help="搜索链接")
    search_parser.add_argument("keyword", help="搜索关键词")

    # tags command
    subparsers.add_parser("tags", help="列出所有标签")

    args = parser.parse_args()

    # Initialize database
    init_db()

    if args.command == "add":
        asyncio.run(add_link(args.url, args.note))
    elif args.command == "list":
        list_links(args.limit)
    elif args.command == "search":
        search_links(args.keyword)
    elif args.command == "tags":
        list_tags()
    else:
        # 无参数时进入交互式模式
        interactive_mode()


if __name__ == "__main__":
    main()
