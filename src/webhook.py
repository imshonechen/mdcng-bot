import asyncio
import logging

from flask import Blueprint, request, jsonify

from .telegram import send_notification

logger = logging.getLogger(__name__)

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"ok": False, "message": "无效的 JSON"}), 400

    event = data.get("event", "")
    if event != "finished":
        return jsonify({"ok": False, "message": f"忽略事件: {event}"}), 400

    bot_token = webhook_bp.config["BOT_TOKEN"]
    chat_id = webhook_bp.config["CHAT_ID"]

    try:
        asyncio.run(send_notification(bot_token, chat_id, data))
    except Exception as e:
        logger.exception("Telegram 发送失败")
        return jsonify({"ok": False, "message": str(e)}), 500

    return jsonify({"ok": True, "message": "通知已发送"}), 200
