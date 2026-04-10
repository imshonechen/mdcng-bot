import logging
import telegram

from .utils import format_date, format_datetime, truncate

logger = logging.getLogger(__name__)


def format_caption(data: dict) -> str:
    """根据刮削数据构建 Telegram 消息文本"""
    event = data.get("event", "finished")
    lines = []

    # 状态标识
    if event == "failed":
        lines.append("<b>[ 刮削失败 ]</b>")
    else:
        lines.append("<b>[ 刮削成功 ]</b>")

    # 影片信息
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
    if data.get("tags"):
        lines.append(f"<b>标签:</b> {data['tags']}")

    # 任务信息
    lines.append("")
    if data.get("task_id"):
        lines.append(f"<b>任务ID:</b> {data['task_id']}")
    if data.get("started_at"):
        lines.append(f"<b>开始时间:</b> {format_datetime(data['started_at'])}")
    if data.get("timestamp"):
        lines.append(f"<b>结束时间:</b> {format_datetime(data['timestamp'])}")
    if data.get("duration"):
        lines.append(f"<b>耗时:</b> {data['duration']}秒")

    # 失败原因
    if event == "failed" and data.get("error_message"):
        lines.append(f"\n<b>失败原因:</b> {data['error_message']}")

    return "\n".join(lines)


async def send_notification(bot_token: str, chat_id: str, data: dict) -> None:
    """发送刮削通知到 Telegram"""
    bot = telegram.Bot(token=bot_token)
    caption = format_caption(data)
    thumb = data.get("thumb", "")

    if thumb:
        try:
            await bot.send_photo(
                chat_id=chat_id,
                photo=thumb,
                caption=caption,
                parse_mode="HTML",
            )
        except telegram.error.BadRequest:
            logger.warning("封面图发送失败，降级为纯文本: %s", thumb)
            await bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode="HTML",
            )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="HTML",
        )

    logger.info("通知已发送: %s", data.get("number", "unknown"))
