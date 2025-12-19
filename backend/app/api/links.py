"""Links API Routes"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from app.database import get_session
from app.models import Link, Tag, TagLinkAssociation
from app.schemas import (
    LinkCreate,
    LinkUpdate,
    LinkResponse,
    LinkListResponse,
    TagResponse,
)
from app.api.auth import require_auth

router = APIRouter(prefix="/links", tags=["links"])


@router.get("", response_model=LinkListResponse)
def get_links(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Get paginated list of links"""
    # Base query
    query = select(Link).order_by(Link.created_at.desc())

    # Filter by tag if provided
    if tag:
        query = (
            query.join(TagLinkAssociation)
            .join(Tag)
            .where(Tag.name == tag)
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Paginate
    offset = (page - 1) * page_size
    links = session.exec(query.offset(offset).limit(page_size)).all()

    return LinkListResponse(
        items=[_link_to_response(link) for link in links],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(links)) < total,
    )


@router.get("/{link_id}", response_model=LinkResponse)
def get_link(link_id: int, session: Session = Depends(get_session)):
    """Get a single link by ID"""
    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return _link_to_response(link)


@router.post("", response_model=LinkResponse, status_code=201)
async def create_link(
    link_data: LinkCreate,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Create a new link and process it with AI. Requires authentication."""
    from app.services.link_processor import link_processor

    link = await link_processor.add_and_process_link(
        url=str(link_data.url),
        user_note=link_data.user_note,
        session=session,
        submitted_by="web",
    )

    return _link_to_response(link)


@router.put("/{link_id}", response_model=LinkResponse)
def update_link(
    link_id: int,
    link_data: LinkUpdate,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Update a link. Requires authentication."""
    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # Update fields
    if link_data.title is not None:
        link.title = link_data.title
    if link_data.description is not None:
        link.description = link_data.description
    if link_data.user_note is not None:
        link.user_note = link_data.user_note

    # Update tags if provided
    if link_data.tag_ids is not None:
        # Clear existing tags
        link.tags = []
        # Add new tags
        for tag_id in link_data.tag_ids:
            tag = session.get(Tag, tag_id)
            if tag:
                link.tags.append(tag)

    link.updated_at = datetime.utcnow()
    session.add(link)
    session.commit()
    session.refresh(link)

    return _link_to_response(link)


@router.delete("/{link_id}", status_code=204)
def delete_link(
    link_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Delete a link. Requires authentication."""
    link = session.get(Link, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    session.delete(link)
    session.commit()


def _link_to_response(link: Link) -> LinkResponse:
    """Convert Link model to response schema"""
    return LinkResponse(
        id=link.id,
        url=link.url,
        title=link.title,
        description=link.description,
        user_note=link.user_note,
        favicon_url=link.favicon_url,
        og_image_url=link.og_image_url,
        domain=link.domain,
        created_at=link.created_at,
        updated_at=link.updated_at,
        is_processed=link.is_processed,
        tags=[TagResponse(id=t.id, name=t.name, color=t.color) for t in link.tags],
    )
