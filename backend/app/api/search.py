"""Search API Routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, or_

from app.database import get_session
from app.models import Link, Tag, TagLinkAssociation
from app.schemas import LinkResponse, LinkListResponse, TagResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=LinkListResponse)
def search_links(
    q: Optional[str] = Query(None, description="Search keyword"),
    tags: Optional[List[str]] = Query(None, description="Filter by tag names"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """
    Search links by keyword and/or tags.

    - `q`: Search in title, description, and user_note
    - `tags`: Filter by tag names (AND logic - must have all specified tags)
    """
    # Base query
    query = select(Link).order_by(Link.created_at.desc())

    # Keyword search
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Link.title.ilike(search_term),
                Link.description.ilike(search_term),
                Link.user_note.ilike(search_term),
                Link.domain.ilike(search_term),
            )
        )

    # Tag filter
    if tags:
        for tag_name in tags:
            # Subquery to find links with this tag
            subquery = (
                select(TagLinkAssociation.link_id)
                .join(Tag)
                .where(Tag.name == tag_name)
            )
            query = query.where(Link.id.in_(subquery))

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
