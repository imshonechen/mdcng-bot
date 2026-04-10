# MDCNG 刮削通知 Telegram Bot — 开发文档

## 1. 项目概述

一个轻量级 Telegram 通知机器人，接收 MDCNG 刮削完成后的 Webhook 回调，将刮削结果（封面、番号、标题、演员等）格式化后推送到指定 Telegram 聊天。

### 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 语言 | Python ≥ 3.10 | 类型提示、match 语法 |
| Web 框架 | Flask | 轻量，接收 Webhook 回调 |
| Telegram SDK | python-telegram-bot | 最主流的 Python TG 库，异步支持完善 |
| 配置管理 | python-dotenv | 通过 `.env` 管理敏感信息 |

---

## 2. 架构

```
MDCNG 刮削完成
      │
      ▼  HTTP POST (JSON)
┌─────────────┐
│   Flask     │  POST /webhook
│   Server    │
└──────┬──────┘
       │ 解析 & 格式化
       ▼
┌─────────────┐
│  Telegram   │  sendPhoto + caption
│  Bot API    │──────► TG 聊天/频道
└─────────────┘
```

**核心流程：**

1. MDCNG 刮削成功 → 向本服务发送 POST 请求
2. Flask 接收请求，校验并提取字段
3. 格式化为 Telegram 消息，调用 Bot API 发送带封面图的通知

---

## 3. 目录结构

```
mdcng-bot/
├── src/
│   ├── app.py            # 入口：启动 Flask 服务
│   ├── webhook.py        # Webhook 路由处理
│   ├── telegram.py       # Telegram 消息发送逻辑
│   └── utils.py          # 工具函数（日期格式化等）
├── .env.example          # 环境变量模板
├── requirements.txt      # Python 依赖
├── DEV.md                # 本文档
└── MDCNG-api.MD          # MDCNG Webhook 接口参考
```

---

## 4. 环境变量

| 变量名 | 必填 | 说明 | 示例 |
|--------|------|------|------|
| `BOT_TOKEN` | 是 | Telegram Bot Token（从 @BotFather 获取） | `123456:ABC-DEF...` |
| `CHAT_ID` | 是 | 接收通知的聊天/频道 ID | `-1001234567890` |
| `PORT` | 否 | Webhook 监听端口，默认 `5000` | `5000` |
| `WEBHOOK_SECRET` | 否 | Webhook 验证密钥（可选安全校验） | `my-secret-key` |

---

## 5. MDCNG Webhook 配置

在 MDCNG 的 Webhook 设置中配置以下内容：

| 字段 | 值 |
|------|------|
| **Request Method** | `POST` |
| **URL** | `http://<服务器IP>:<PORT>/webhook` |
| **触发事件** | `finished`（仅刮削成功） |
| **Headers** | `Content-Type: application/json` |

**Body 模板：**

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
    "tags": "{{ tags }}",
    "thumb": "{{ thumb }}",
    "task_id": "{{ task_id }}",
    "duration": "{{ duration }}",
    "started_at": "{{ started_at }}",
    "timestamp": "{{ timestamp }}",
    "error_message": "{{ error_message }}"
}
```

---

## 6. Telegram 消息模板

使用 `sendPhoto` 方法发送带封面图的消息，`parse_mode` 设为 `HTML`。

**消息格式：**

```
番号: ABC-001
标题: 示例标题
演员: 演员A, 演员B
发行日期: 2025年3月15日
简介: 这是一段简介文字...
片长: 120分钟
分类: 有码
系列: 某系列
```

**格式化规则：**

| 字段 | 处理逻辑 |
|------|----------|
| 封面图 | 使用 `thumb` 作为 `sendPhoto` 的 `photo` 参数；缺失时降级为 `sendMessage` |
| 发行日期 | 将 `release`（如 `2025-03-15`）格式化为 `2025年3月15日` |
| 简介 | 截断至 200 字符，超出部分以 `...` 结尾 |
| 缺失字段 | 显示为空或整行不显示 |

---

## 7. API 接口

### `POST /webhook`

接收 MDCNG 的刮削通知。

**Request：**

```
Content-Type: application/json
```

```json
{
    "event": "finished",
    "number": "ABC-001",
    "title": "示例标题",
    "actor": "演员A",
    "release": "2025-03-15",
    "outline": "简介内容...",
    "runtime": "120",
    "category": "有码",
    "series": "某系列",
    "thumb": "https://example.com/cover.jpg"
}
```

**Response：**

| 状态码 | 说明 |
|--------|------|
| `200` | 通知发送成功 |
| `400` | 请求体缺少必要字段或 event 不为 finished |
| `500` | Telegram 发送失败 |

```json
{ "ok": true, "message": "通知已发送" }
```

---

## 8. 核心逻辑说明

### 8.1 Webhook 处理 (`webhook.py`)

```
接收 POST /webhook
  → 校验 event == "finished"
  → 提取字段 (number, title, actor, release, outline, runtime, category, series, thumb)
  → 调用 telegram.send_notification(data)
  → 返回 200
```

### 8.2 Telegram 发送 (`telegram.py`)

```
send_notification(data):
  → format_caption(data)         # 构建消息文本
  → 判断 thumb 是否存在
    → 有: bot.send_photo(chat_id, photo=thumb, caption=caption, parse_mode="HTML")
    → 无: bot.send_message(chat_id, text=caption, parse_mode="HTML")
```

### 8.3 日期格式化 (`utils.py`)

```
format_date("2025-03-15") → "2025年3月15日"
format_date("")           → ""
```

---

## 9. 开发步骤

1. **初始化项目** — 创建虚拟环境，`pip install flask python-telegram-bot python-dotenv`
2. **实现 `src/telegram.py`** — 初始化 Bot 实例，封装 `send_notification`
3. **实现 `src/utils.py`** — 日期格式化、简介截断等工具函数
4. **实现 `src/webhook.py`** — Flask 路由，解析请求并调用发送
5. **实现 `src/app.py`** — 组装启动 Flask 服务
6. **配置 MDCNG Webhook** — 按第 5 节配置 Body 模板和 URL
7. **测试** — 使用 MDCNG 的「测试」按钮或 `curl` 手动发送请求验证

---

## 10. 测试命令

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
