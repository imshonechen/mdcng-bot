# MDCNG Telegram 通知机器人

接收 [MDCNG](https://github.com/mdc-ng/mdc-ng) 刮削完成后的 Webhook 通知，将结果推送到 Telegram。

**通知效果：**

```
┌──────────────────────┐
│      [封面图片]       │
│                      │
│ 番号: ABC-001        │
│ 标题: 示例标题        │
│ 演员: 演员A, 演员B   │
│ 发行日期: 2025年3月15日│
│ 简介: 这是一段简介... │
│ 片长: 120分钟         │
│ 分类: 有码            │
│ 系列: 某系列          │
└──────────────────────┘
```

## 快速开始

### 1. 前置准备

- Python ≥ 3.10
- 一个 Telegram Bot Token（通过 [@BotFather](https://t.me/BotFather) 创建）
- 接收通知的聊天/频道 ID

### 2. 安装

```bash
git clone https://github.com/your-username/mdcng-bot.git
cd mdcng-bot
pip install -r requirements.txt
```

### 3. 配置

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
BOT_TOKEN=123456:ABC-DEF...       # Telegram Bot Token
CHAT_ID=-1001234567890             # 聊天/频道 ID
PORT=5000                          # 监听端口（可选，默认 5000）
```

### 4. 启动

```bash
python -m src.app
```

服务将监听 `0.0.0.0:5000`。

## Docker 部署

### 方式一：从源码构建

```bash
git clone https://github.com/imshonechen/mdcng-bot.git
cd mdcng-bot
cp .env.example .env
# 编辑 .env 填入 BOT_TOKEN 和 CHAT_ID
docker compose up -d
```

### 方式二：使用 GHCR 镜像

无需克隆仓库，创建一个 `docker-compose.yml`：

```yaml
services:
  mdcng-bot:
    image: ghcr.io/imshonechen/mdcng-bot:latest
    container_name: mdcng-bot
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - BOT_TOKEN=你的Token
      - CHAT_ID=你的ChatID
```

然后启动：

```bash
docker compose up -d
```

## MDCNG Webhook 配置

在 MDCNG 的 Webhook 设置中填入：

| 字段 | 值 |
|------|------|
| Request Method | `POST` |
| URL | `http://<服务器IP>:5000/webhook` |
| 触发事件 | `finished` |
| Headers | `Content-Type: application/json` |

Body 模板：

```json
{
    "event": "{{ event }}",
    "number": "{{ number }}",
    "title": "{{ title }}",
    "actor": "{{ actor }}",
    "release": "{{ release }}",
    "outline": "{{ outline }}",
    "runtime": "{{ runtime }}",
    "category": "{{ category }}",
    "series": "{{ series }}",
    "thumb": "{{ thumb }}"
}
```

## 测试

使用 curl 手动测试：

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "finished",
    "number": "ABC-001",
    "title": "示例标题",
    "actor": "演员A, 演员B",
    "release": "2025-03-15",
    "outline": "这是一段简介文字，用于测试消息推送效果。",
    "runtime": "120",
    "category": "有码",
    "series": "某系列",
    "thumb": "https://via.placeholder.com/300x400"
  }'
```

## 项目结构

```
mdcng-bot/
├── src/
│   ├── app.py          # 入口：启动 Flask 服务
│   ├── webhook.py      # Webhook 路由处理
│   ├── telegram.py     # Telegram 消息发送
│   └── utils.py        # 工具函数
├── .env.example        # 环境变量模板
├── requirements.txt    # Python 依赖
├── Dockerfile
├── docker-compose.yml
└── DEV.md              # 开发文档
```

## License

MIT
