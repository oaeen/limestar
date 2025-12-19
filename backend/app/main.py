"""LimeStar - Link Collection System

FastAPI main application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import links, tags, search, admin
from app.bot.telegram_bot import process_webhook_update, setup_webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    init_db()

    # 如果配置了 WEBHOOK_URL，自动设置 Telegram Webhook
    if settings.WEBHOOK_URL and settings.TELEGRAM_BOT_TOKEN:
        try:
            await setup_webhook(settings.WEBHOOK_URL)
            print(f"Telegram Webhook 已设置: {settings.WEBHOOK_URL}")
        except Exception as e:
            print(f"设置 Telegram Webhook 失败: {e}")

    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="LimeStar",
    description="AI-powered link collection system with Chinese summaries and auto-tagging",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(links.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "LimeStar",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Telegram Webhook 端点
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """处理 Telegram Webhook 请求"""
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"ok": False, "error": "Bot not configured"}

    try:
        data = await request.json()
        return await process_webhook_update(data)
    except Exception as e:
        print(f"Webhook 处理错误: {e}")
        return {"ok": False, "error": str(e)}
