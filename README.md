# LimeStar 🍋⭐

AI 驱动的链接收藏系统，自动生成中文介绍和标签。

![LimeStar Screenshot](limestar_screenshot.png)

## 功能特点

- 📎 保存链接并自动抓取网页内容
- 🤖 AI 自动生成中文介绍和标签
- 🏷️ 标签分类和关键词搜索
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

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python run.py
```

后端服务将在 http://localhost:8000 启动

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 4. 通过 CLI 添加链接

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

## 项目结构

```
limestar/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── services/     # 业务服务
│   │   ├── models.py     # 数据模型
│   │   └── main.py       # FastAPI 入口
│   ├── cli.py            # 命令行工具
│   └── run.py            # 启动脚本
├── frontend/
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── hooks/        # 自定义 Hooks
│   │   └── styles/       # 样式文件
│   └── package.json
└── README.md
```

## 配置说明

在 `.env` 文件中配置：

```env
# OpenAI API (支持自定义 base_url)
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4o-mini
```

## License

MIT
