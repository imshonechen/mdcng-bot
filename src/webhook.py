import asyncio
import logging

from flask import Blueprint, request, jsonify
from telegram.error import BadRequest, Forbidden, InvalidToken

from .telegram import send_notification

logger = logging.getLogger(__name__)

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook", methods=["GET"])
def health_check():
    return jsonify({"ok": True, "message": "mdcng-bot 运行中"}), 200


@webhook_bp.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"ok": False, "message": "请求体不是有效的 JSON 格式"}), 400

    event = data.get("event", "")
    if event != "finished":
        return jsonify({"ok": False, "message": f"已忽略事件类型: {event}，仅处理 finished"}), 400

    bot_token = webhook_bp.config["BOT_TOKEN"]
    chat_id = webhook_bp.config["CHAT_ID"]

    try:
        asyncio.run(send_notification(bot_token, chat_id, data))
    except InvalidToken:
        return jsonify({
            "ok": False,
            "message": "BOT_TOKEN 无效，请检查配置",
            "排查步骤": [
                "1. 通过 @BotFather 确认 Token 是否正确",
                "2. 检查 .env 或 docker-compose.yml 中的 BOT_TOKEN 是否完整",
            ],
        }), 500
    except (BadRequest, Forbidden) as e:
        error_msg = str(e)
        if "Chat not found" in error_msg or "chat not found" in error_msg:
            return jsonify({
                "ok": False,
                "message": "CHAT_ID 配置不正确，找不到目标聊天",
                "排查步骤": [
                    "1. 私聊: 先向 Bot 发送 /start，然后访问 https://api.telegram.org/bot<BOT_TOKEN>/getUpdates 获取 chat.id",
                    "2. 群组: 将 Bot 加入群组，在群内发送一条消息，再通过上述 getUpdates 接口获取 chat.id（通常为负数）",
                    "3. 频道: 将 Bot 设为频道管理员，CHAT_ID 填频道的 @用户名 或数字 ID",
                    "4. 更新 .env 或 docker-compose.yml 中的 CHAT_ID 后重启服务",
                ],
            }), 500
        if "Forbidden" in error_msg:
            return jsonify({
                "ok": False,
                "message": "Bot 没有权限发送消息到目标聊天",
                "排查步骤": [
                    "1. 确认 Bot 已加入目标群组或频道",
                    "2. 频道需将 Bot 设为管理员",
                    "3. 私聊需先向 Bot 发送 /start",
                ],
            }), 500
        return jsonify({"ok": False, "message": f"Telegram 请求失败: {error_msg}"}), 500
    except Exception as e:
        logger.exception("Telegram 发送失败")
        return jsonify({"ok": False, "message": f"发送失败: {e}"}), 500

    return jsonify({"ok": True, "message": "通知已发送"}), 200
