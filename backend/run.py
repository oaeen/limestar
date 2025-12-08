#!/usr/bin/env python3
"""
LimeStar Backend Server

Usage:
    python run.py

This will start the FastAPI server on http://localhost:8000
"""

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
