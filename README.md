# LimeStar

AI 驱动的链接收藏系统，自动生成中文介绍和标签。

![LimeStar Screenshot](limestar_screenshot.png)

## 功能特点

- 📎 保存链接并自动抓取网页内容
- 🤖 AI 自动生成中文介绍和标签
- 🏷️ 标签分类和关键词搜索
- 🤖 Telegram Bot 支持
- 🎨 Apple Liquid Glass 设计风格
- 📱 移动端响应式适配

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python + FastAPI |
| 数据库 | SQLite + SQLModel |
| AI | OpenAI API (可自定义) |
| 前端 | React + TypeScript + Vite |
| 样式 | Tailwind CSS + Framer Motion |
| Bot | python-telegram-bot |

---

## 快速开始（本地开发）

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入 API Key 和 Bot Token
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

后端服务：http://localhost:8000

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端服务：http://localhost:3000

### 4. 启动 Telegram Bot（可选）

```bash
cd backend
python run_bot.py
```

---

## Docker 部署

### 1. 配置环境变量

```bash
cp .env.example .env
nano .env
```

关键配置：
```env
OPENAI_API_KEY=your-api-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-user-id
WEBHOOK_URL=https://star.cug.life/telegram/webhook
```

### 2. 启动服务

```bash
docker-compose up -d --build
```

### 3. 配置外部 Nginx

```nginx
server {
    listen 80;
    server_name star.cug.life;

    # API 和 Webhook
    location /api {
        proxy_pass http://127.0.0.1:18765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }

    location /telegram/webhook {
        proxy_pass http://127.0.0.1:18765;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://127.0.0.1:18765;
    }

    # 前端
    location / {
        proxy_pass http://127.0.0.1:18766;
        proxy_set_header Host $host;
    }
}
```

### 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| backend | 18765 | API + Telegram Webhook |
| frontend | 18766 | 前端静态文件 |

---

## Telegram Bot 使用

### 获取 Token 和用户 ID

1. 在 Telegram 中搜索 [@BotFather](https://t.me/BotFather)，创建 Bot 获取 Token
2. 搜索 [@userinfobot](https://t.me/userinfobot)，获取你的用户 ID

### 命令列表

| 命令 | 说明 |
|------|------|
| `/start` | 显示欢迎和帮助 |
| `/help` | 使用帮助 |
| `/list [n]` | 显示最近 n 条收藏 |
| `/search <关键词>` | 搜索收藏 |

### 收藏链接

直接发送链接即可，支持附带备注：

```
https://example.com 这是一个很棒的工具
```

---

## CLI 命令行工具

```bash
cd backend

# 添加链接
python cli.py add https://example.com

# 添加链接并附带备注
python cli.py add https://example.com --note "这是一个很棒的网站"

# 查看所有链接
python cli.py list

# 搜索链接
python cli.py search AI

# 查看所有标签
python cli.py tags
```

---

## API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /api/links | 获取链接列表 |
| GET | /api/links/{id} | 获取单个链接 |
| POST | /api/links | 创建链接 |
| PUT | /api/links/{id} | 更新链接 |
| DELETE | /api/links/{id} | 删除链接 |
| GET | /api/tags | 获取所有标签 |
| GET | /api/search | 搜索链接 |
| POST | /telegram/webhook | Telegram Webhook |

---

## 项目结构

```
limestar/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── bot/          # Telegram Bot
│   │   ├── services/     # 业务服务
│   │   ├── models.py     # 数据模型
│   │   └── main.py       # FastAPI 入口
│   ├── cli.py            # 命令行工具
│   ├── run.py            # 后端启动脚本
│   └── run_bot.py        # Bot 启动脚本（Polling 模式）
├── frontend/
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── hooks/        # 自定义 Hooks
│   │   └── styles/       # 样式文件
│   ├── Dockerfile
│   └── package.json
├── Dockerfile            # 后端 Docker 镜像
├── docker-compose.yml    # Docker 编排
└── README.md
```

---

## 配置说明

```env
# 数据库
DATABASE_URL=sqlite:///./limestar.db

# OpenAI API (支持 DeepSeek 等兼容 API)
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4o-mini

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=123456789  # 白名单，逗号分隔
WEBHOOK_URL=https://star.cug.life/telegram/webhook  # 生产环境
```

## License

MIT
