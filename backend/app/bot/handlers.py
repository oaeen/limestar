"""Telegram Bot Handlers - 命令和消息处理器"""

import re
import html
import asyncio
from functools import wraps
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlmodel import Session, select, desc
from sqlalchemy import delete

from app.config import settings
from app.database import engine
from app.models import Link, Tag, TagLinkAssociation
from app.services.link_processor import link_processor


def escape_html(text: str) -> str:
    """转义 HTML 特殊字符"""
    return html.escape(text)


# 重建状态追踪
_rebuild_status = {
    "running": False,
    "processed": 0,
    "total": 0,
    "current_url": None,
}


# URL 正则表达式
URL_PATTERN = re.compile(
    r'https?://[^\s<>"{}|\\^`\[\]]+|'
    r'(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s<>"{}|\\^`\[\]]*)?'
)


def require_auth(func):
    """白名单权限检查装饰器"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        allowed = settings.get_allowed_users()
        if allowed and user_id not in allowed:
            await update.message.reply_text("无权限使用此 Bot")
            return
        return await func(update, context)
    return wrapper


@require_auth
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    welcome_text = """LimeStar - 链接收藏助手

直接发送链接即可自动收藏，AI 会为你生成中文标题、描述和标签。

命令列表：
/list [n] - 显示最近 n 条收藏（默认 5）
/search <关键词> - 搜索收藏
/rebuild_tags - 重建所有标签（需确认）
/rebuild_status - 查看重建进度
/help - 显示帮助

小技巧：
- 链接后可附带备注，如：
  https://example.com 这是一个好工具"""
    await update.message.reply_text(welcome_text)


@require_auth
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = """使用帮助

收藏链接：
直接发送链接，可附带备注
例：https://github.com 代码托管平台

查看收藏：
/list - 显示最近 5 条
/list 10 - 显示最近 10 条

搜索收藏：
/search <关键词>
例：/search github

标签管理：
/rebuild_tags - 清除并重建所有标签
/rebuild_status - 查看重建进度"""
    await update.message.reply_text(help_text)


@require_auth
async def list_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /list 命令 - 显示最近收藏"""
    # 解析数量参数
    limit = 5
    if context.args:
        try:
            limit = min(int(context.args[0]), 20)  # 最多 20 条
        except ValueError:
            pass

    with Session(engine) as session:
        links = session.exec(
            select(Link)
            .where(Link.is_processed == True)
            .order_by(desc(Link.created_at))
            .limit(limit)
        ).all()

        if not links:
            await update.message.reply_text("暂无收藏")
            return

        # 构建消息（使用 HTML 格式避免特殊字符问题）
        lines = [f"最近收藏 (共 {len(links)} 条)\n"]
        for i, link in enumerate(links, 1):
            date_str = link.created_at.strftime("%m-%d")
            # 标题作为超链接（HTML 格式）
            title_escaped = escape_html(link.title)
            lines.append(f'{i}. <a href="{link.url}">{title_escaped}</a>')
            lines.append(f"   {link.domain} | {date_str}\n")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML")


@require_auth
async def search_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /search 命令 - 搜索收藏"""
    if not context.args:
        await update.message.reply_text("请输入搜索关键词\n例：/search github")
        return

    keyword = " ".join(context.args)

    with Session(engine) as session:
        # 简单的 LIKE 搜索
        pattern = f"%{keyword}%"
        links = session.exec(
            select(Link)
            .where(Link.is_processed == True)
            .where(
                (Link.title.contains(keyword)) |
                (Link.description.contains(keyword)) |
                (Link.url.contains(keyword))
            )
            .order_by(desc(Link.created_at))
            .limit(10)
        ).all()

        if not links:
            await update.message.reply_text(f'未找到包含 "{keyword}" 的收藏')
            return

        # 构建消息（使用 HTML 格式避免特殊字符问题）
        lines = [f'搜索结果: "{escape_html(keyword)}"\n']
        lines.append(f"找到 {len(links)} 条匹配:\n")
        for i, link in enumerate(links, 1):
            # 标题作为超链接（HTML 格式）
            title_escaped = escape_html(link.title)
            lines.append(f'{i}. <a href="{link.url}">{title_escaped}</a>')
            # 截取描述片段
            desc_text = link.description[:50] + "..." if len(link.description) > 50 else link.description
            lines.append(f"   {escape_html(desc_text)}")
            # 显示标签
            if link.tags:
                tag_names = " | ".join(t.name for t in link.tags[:3])
                lines.append(f"   {tag_names}\n")
            else:
                lines.append("")

        await update.message.reply_text("\n".join(lines), parse_mode="HTML")


def extract_url_and_note(text: str) -> tuple[Optional[str], Optional[str]]:
    """从文本中提取 URL 和用户备注"""
    match = URL_PATTERN.search(text)
    if not match:
        return None, None

    url = match.group(0)
    # URL 后的文本作为备注
    note = text[match.end():].strip()
    return url, note if note else None


@require_auth
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息 - 检测并收藏链接"""
    text = update.message.text
    if not text:
        return

    url, user_note = extract_url_and_note(text)
    if not url:
        return  # 没有链接，忽略

    # 发送处理中提示
    processing_msg = await update.message.reply_text("正在处理链接...")

    try:
        with Session(engine) as session:
            link = await link_processor.add_and_process_link(
                url=url,
                user_note=user_note,
                session=session,
                submitted_by="telegram",
            )

            # 构建成功消息
            lines = ["已收藏！\n"]
            lines.append(f"{link.title}")
            lines.append(f"{link.description}\n")

            if link.tags:
                tag_names = " | ".join(t.name for t in link.tags)
                lines.append(f"{tag_names}")

            await processing_msg.edit_text("\n".join(lines))

    except Exception as e:
        await processing_msg.edit_text(f"处理失败: {str(e)}")


@require_auth
async def rebuild_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /rebuild_tags 命令 - 重建所有标签（带二次确认）"""
    global _rebuild_status

    # 检查是否正在运行
    if _rebuild_status["running"]:
        progress = f"{_rebuild_status['processed']}/{_rebuild_status['total']}"
        await update.message.reply_text(
            f"标签重建正在进行中...\n"
            f"进度: {progress}\n"
            f"当前: {_rebuild_status['current_url'] or '准备中'}"
        )
        return

    # 获取链接总数
    with Session(engine) as session:
        total = len(session.exec(select(Link.id)).all())

    if total == 0:
        await update.message.reply_text("没有需要处理的链接")
        return

    # 发送确认按钮
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("确认重建", callback_data="rebuild_confirm"),
            InlineKeyboardButton("取消", callback_data="rebuild_cancel"),
        ]
    ])

    await update.message.reply_text(
        f"⚠️ <b>标签重建确认</b>\n\n"
        f"即将执行以下操作：\n"
        f"1. 清除所有现有标签和分类\n"
        f"2. 重新处理所有 {total} 条链接\n"
        f"3. 使用AI重新生成标签\n\n"
        f"这个操作可能需要较长时间，确定要继续吗？",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def handle_rebuild_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理重建确认回调"""
    global _rebuild_status

    query = update.callback_query
    await query.answer()

    if query.data == "rebuild_cancel":
        await query.edit_message_text("已取消标签重建")
        return

    if query.data == "rebuild_confirm":
        # 再次检查是否正在运行
        if _rebuild_status["running"]:
            await query.edit_message_text("标签重建已在运行中，请稍候...")
            return

        await query.edit_message_text("正在启动标签重建...")

        # 启动后台任务
        asyncio.create_task(_do_rebuild_tags(query))


async def _do_rebuild_tags(query):
    """执行标签重建的后台任务"""
    global _rebuild_status

    try:
        _rebuild_status["running"] = True
        _rebuild_status["processed"] = 0

        # Step 1: 清除所有标签
        with Session(engine) as session:
            session.exec(delete(TagLinkAssociation))
            session.exec(delete(Tag))
            session.commit()

        await query.edit_message_text("已清除旧标签，开始重新处理链接...")

        # Step 2: 获取所有链接
        with Session(engine) as session:
            links = session.exec(select(Link.id, Link.url)).all()
            _rebuild_status["total"] = len(links)

        # Step 3: 逐个重新处理
        for i, (link_id, url) in enumerate(links):
            _rebuild_status["processed"] = i
            _rebuild_status["current_url"] = url

            try:
                with Session(engine) as session:
                    link = session.get(Link, link_id)
                    if link:
                        link.is_processed = False
                        link.tags = []
                        session.add(link)
                        session.commit()

                        await link_processor.process_link(link_id, session)

            except Exception as e:
                print(f"重建标签失败 [{link_id}] {url}: {e}")
                continue

            # 每处理10个更新一次进度
            if (i + 1) % 10 == 0:
                try:
                    await query.edit_message_text(
                        f"标签重建进行中...\n"
                        f"进度: {i + 1}/{_rebuild_status['total']}\n"
                        f"当前: {url[:50]}..."
                    )
                except Exception:
                    pass  # 忽略消息编辑错误

            # 避免请求过快
            await asyncio.sleep(0.5)

        # 完成
        _rebuild_status["processed"] = _rebuild_status["total"]
        _rebuild_status["current_url"] = None

        await query.edit_message_text(
            f"标签重建完成！\n"
            f"共处理 {_rebuild_status['total']} 条链接"
        )

    except Exception as e:
        await query.edit_message_text(f"标签重建失败: {str(e)}")

    finally:
        _rebuild_status["running"] = False


@require_auth
async def rebuild_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /rebuild_status 命令 - 查看重建状态"""
    global _rebuild_status

    if not _rebuild_status["running"]:
        await update.message.reply_text("当前没有正在进行的标签重建任务")
        return

    progress = f"{_rebuild_status['processed']}/{_rebuild_status['total']}"
    percent = int(_rebuild_status['processed'] / _rebuild_status['total'] * 100) if _rebuild_status['total'] > 0 else 0

    await update.message.reply_text(
        f"标签重建进行中...\n"
        f"进度: {progress} ({percent}%)\n"
        f"当前: {_rebuild_status['current_url'] or '准备中'}"
    )
