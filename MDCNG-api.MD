# MDCNG Webhook & 命名模板 参考文档

> [MDCNG](https://github.com/mdc-ng/mdc-ng) — 成人影视元数据刮削工具。  
> 本文档整理其 **Webhook 通知接口** 和 **命名模板** 的配置说明。

---

## 一、Webhook 通知

配置并开启后，当刮削任务完成或失败时，MDC 会向指定端点发送 HTTP 请求通知。  
支持添加**多个端点**。

### 1.1 基本配置

| 字段 | 说明 |
|------|------|
| **Name** | 端点名称 |
| **Request Method** | `POST` / `GET` / `PUT` / `PATCH` |
| **URL** | 支持模板变量，如 `https://example.com/api?number={{number}}` |
| **超时 (秒)** | 默认 `10s` |

### 1.2 触发条件

| 字段 | 说明 |
|------|------|
| **触发事件** | `finished`（刮削成功）/ `failed`（刮削失败），支持单选或多选 |
| **触发分类** | 勾选指定分类触发；不勾选则所有分类都触发 |
| **高级触发条件** | minijinja 表达式，可用变量与 Body 模板一致 |

高级触发条件示例：

```jinja
category == '有码'
'PRESTIGE' in studio
year | int >= 2025
```

### 1.3 请求头 (Headers)

自定义请求头，示例：

```
Content-Type: application/json
```

### 1.4 Body 模板 (JSON)

使用 **Jinja2 模板语法**（如 `{{ number }}`），变量不存在时渲染为空字符串。

**可用变量分类：**

| 分类 | 变量 |
|------|------|
| **事件信息** | `event`（finished / failed）、`timestamp`（完成时间）、`started_at`（开始时间） |
| **任务信息** | `task_id`、`duration`（耗时秒数）、`source_path`、`target_path`、`error_message` |
| **刮削数据** | `number`、`title`、`actor`、`first_actor`、`category`、`subtitle`、`mosaic`、`resolution`、`tags`、`outline`、`thumb`（封面 URL）、`poster`（海报 URL）等 |

> 刮削数据变量与命名设置中的变量一致，完整列表详见下方[可用变量表](#三可用变量表)。

**Body 示例：**

```json
{
    "event": "{{ event }}",
    "data": {
        "title": "{{ title }}"
    }
}
```

### 1.5 自定义测试变量

JSON 格式，用于覆盖默认测试变量。留空则使用内置测试数据。

```json
{"number": "ABC-123", "title": "自定义标题"}
```

---

## 二、命名设置

### 2.1 模板语法

命名规则支持两种语法：

| 语法 | 格式 | 缺失字段处理 | 特性 |
|------|------|-------------|------|
| **基础语法** | `{number}` | 显示 `未知` | — |
| **高级语法 (Jinja2)** | `{{ number }}` | 显示为空 | 支持条件判断和 filter |

### 2.2 常用 Filter

| 示例 | 说明 |
|------|------|
| `{{ studio \| default("独立") }}` | 缺失时使用默认值 |
| `{{ number \| upper }}` | 转大写 |
| `{{ number \| lower }}` | 转小写 |
| `{{ title \| truncate(20) }}` | 截断超长文本 |
| `{{ number \| split("-") \| first }}` | 拆分取首段 |
| `{{ number \| split("-") \| last }}` | 拆分取末段 |
| `{{ title \| replace("A", "B") }}` | 替换文本 |
| `{{ " text " \| trim }}` | 去除首尾空格 |

### 2.3 条件判断

```jinja
{# 有值时才显示 #}
{% if series %}{{ series }}/{% endif %}

{# 有值/无值分别处理 #}
{% if director %}{{ director }}{% else %}未知{% endif %}
```

### 2.4 实用模板示例

| 模板 | 说明 |
|------|------|
| `{{ number }}{% if publish_number %} ({{ publish_number }}){% endif %}` | 有发行号时附加括号 |
| `{{ actor \| default(studio \| default("未知")) }}` | 多级降级：演员 → 制片方 → 固定值 |
| `{{ category }}/{{ number \| split("-") \| first }}/{{ number }}` | 按分类和番号前缀归档 |

### 2.5 AI 辅助生成

配置 LLM 后，命名输入框右侧会出现 **✦** 按钮。清空输入框，输入自然语言描述，点击按钮即可自动生成 Jinja2 模板。

> **示例提示：** "按分类、演员分目录，但分类包含 FC2 和素人时不需要演员目录"

---

## 三、可用变量表

| 变量 | 说明 | 示例 |
|------|------|------|
| `number` | 番号 | `ABS-001` |
| `publish_number` | 发行号 | `118abs001` |
| `series_name` | 番号前缀 | `ABS` |
| `serial_number` | 番号后缀 | `001` |
| `first_letter` | 番号前缀首字母 | `A` |
| `series` | 系列 | |
| `category` | 分类 | |
| `actor` | 演员 | |
| `first_actor` | 首位演员 | |
| `title` | 标题 | |
| `originaltitle` | 原标题 | |
| `year` | 发布年份 | |
| `director` | 导演 | |
| `studio` | 制片方 | |
| `publisher` | 发行方 | |
| `runtime` | 时长 (分钟) | |
| `release` | 发布日期 | |
| `source_filename` | 源文件名 (不含扩展名) | |
| `filename` | 源文件名别名（等同于 `source_filename`） | |
| `source_path` | 源文件完整路径 | |
| `subtitle` | 中文字幕标识 | |
| `mosaic` | 有码/无码标识 | |
| `resolution` | 分辨率 | |

> **Webhook 额外变量：** `tags`、`outline`、`thumb`（封面 URL）、`poster`（海报 URL）
