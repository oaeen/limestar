"""Admin API Routes - Management operations"""

import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlmodel import Session, select
from pydantic import BaseModel

from app.database import get_session, engine
from app.models import Link, Tag, TagLinkAssociation
from app.api.auth import require_auth

router = APIRouter(prefix="/admin", tags=["admin"])


class ReprocessResponse(BaseModel):
    status: str
    total: int
    message: str


class ReprocessStatus(BaseModel):
    processed: int
    total: int
    current_url: Optional[str] = None
    status: str


# Global status tracker
_reprocess_status = {
    "processed": 0,
    "total": 0,
    "current_url": None,
    "status": "idle",
}


@router.post("/reprocess-all", response_model=ReprocessResponse)
async def reprocess_all_links(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """
    Reprocess all links with the new hierarchical tagging system.
    This runs as a background task. Requires authentication.
    """
    global _reprocess_status

    if _reprocess_status["status"] == "running":
        return ReprocessResponse(
            status="already_running",
            total=_reprocess_status["total"],
            message="批量重处理已在运行中，请等待完成",
        )

    # Get all link IDs
    links = session.exec(select(Link.id, Link.url)).all()
    total = len(links)

    if total == 0:
        return ReprocessResponse(
            status="empty",
            total=0,
            message="没有需要处理的链接",
        )

    # Reset status
    _reprocess_status = {
        "processed": 0,
        "total": total,
        "current_url": None,
        "status": "running",
    }

    # Start background task
    background_tasks.add_task(
        batch_reprocess_links,
        [(link_id, url) for link_id, url in links],
    )

    return ReprocessResponse(
        status="started",
        total=total,
        message=f"批量重处理已开始，共 {total} 条链接。可通过 /api/admin/reprocess-status 查看进度",
    )


@router.get("/reprocess-status", response_model=ReprocessStatus)
def get_reprocess_status():
    """Get the current status of batch reprocessing"""
    return ReprocessStatus(**_reprocess_status)


@router.post("/clear-tags")
def clear_all_tags(
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Clear all tags and associations (use before reprocessing). Requires authentication."""
    from sqlalchemy import delete

    # Delete all tag-link associations
    session.exec(delete(TagLinkAssociation))

    # Delete all tags
    session.exec(delete(Tag))

    session.commit()

    return {"status": "success", "message": "所有标签已清除"}


async def batch_reprocess_links(link_data: list):
    """Background task to reprocess all links"""
    global _reprocess_status

    from app.services.link_processor import link_processor

    for i, (link_id, url) in enumerate(link_data):
        _reprocess_status["current_url"] = url
        _reprocess_status["processed"] = i

        try:
            with Session(engine) as session:
                # Reset link processing status
                link = session.get(Link, link_id)
                if link:
                    link.is_processed = False
                    link.tags = []
                    session.add(link)
                    session.commit()

                    # Reprocess
                    await link_processor.process_link(link_id, session)
                    print(f"[{i+1}/{len(link_data)}] 已处理: {url}")

        except Exception as e:
            print(f"[{i+1}/{len(link_data)}] 处理失败 {url}: {e}")
            continue

        # Small delay to avoid overwhelming the AI API
        await asyncio.sleep(0.5)

    _reprocess_status["processed"] = len(link_data)
    _reprocess_status["current_url"] = None
    _reprocess_status["status"] = "completed"
    print(f"批量重处理完成！共处理 {len(link_data)} 条链接")
