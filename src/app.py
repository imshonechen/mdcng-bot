import os
import logging

from dotenv import load_dotenv
from flask import Flask

from .webhook import webhook_bp

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> Flask:
    app = Flask(__name__)

    bot_token = os.getenv("BOT_TOKEN", "")
    chat_id = os.getenv("CHAT_ID", "")

    if not bot_token or not chat_id:
        raise RuntimeError("请在 .env 中配置 BOT_TOKEN 和 CHAT_ID")

    webhook_bp.config = {"BOT_TOKEN": bot_token, "CHAT_ID": chat_id}
    app.register_blueprint(webhook_bp)

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app = create_app()
    app.run(host="0.0.0.0", port=port)
