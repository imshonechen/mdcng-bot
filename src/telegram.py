import logging
import telegram

from .utils import format_date, truncate

logger = logging.getLogger(__name__)


def format_caption(data: dict) -> str:
    """根据刮削数据构建 Telegram 消息文本"""
    lines = []

    if data.get("number"):
        lines.append(f"<b>番号:</b> {data['number']}")
    if data.get("title"):
        lines.append(f"<b>标题:</b> {data['title']}")
    if data.get("actor"):
        lines.append(f"<b>演员:</b> {data['actor']}")
    if data.get("release"):
        lines.append(f"<b>发行日期:</b> {format_date(data['release'])}")
    if data.get("outline"):
        lines.append(f"<b>简介:</b> {truncate(data['outline'])}")
    if data.get("runtime"):
        lines.append(f"<b>片长:</b> {data['runtime']}分钟")
    if data.get("category"):
        lines.append(f"<b>分类:</b> {data['category']}")
    if data.get("series"):
        lines.append(f"<b>系列:</b> {data['series']}")

    return "\n".join(lines)


async def send_notification(bot_token: str, chat_id: str, data: dict) -> None:
    """发送刮削通知到 Telegram"""
    bot = telegram.Bot(token=bot_token)
    caption = format_caption(data)
    thumb = data.get("thumb", "")

    if thumb:
        await bot.send_photo(
            chat_id=chat_id,
            photo=thumb,
            caption=caption,
            parse_mode="HTML",
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="HTML",
        )

    logger.info("通知已发送: %s", data.get("number", "unknown"))
