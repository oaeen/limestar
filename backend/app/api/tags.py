"""Tags API Routes"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from app.database import get_session
from app.models import Tag, TagLinkAssociation
from app.schemas import TagCreate, TagResponse, TagWithCount, CategoryWithTags
from app.api.auth import require_auth

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=List[TagWithCount])
def get_tags(
    include_categories: bool = Query(False, description="Include category tags"),
    session: Session = Depends(get_session),
):
    """Get all tags with link counts (sub-tags only by default)"""
    # Query tags with count
    query = (
        select(Tag, func.count(TagLinkAssociation.link_id).label("count"))
        .outerjoin(TagLinkAssociation)
        .group_by(Tag.id)
        .order_by(func.count(TagLinkAssociation.link_id).desc())
    )

    if not include_categories:
        query = query.where(Tag.is_category == False)

    results = session.exec(query).all()

    return [
        TagWithCount(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            parent_id=tag.parent_id,
            is_category=tag.is_category,
            count=count,
        )
        for tag, count in results
    ]


@router.get("/categories", response_model=List[CategoryWithTags])
def get_categories_with_tags(session: Session = Depends(get_session)):
    """Get all categories with their child tags (hierarchical view)"""
    # 1. Get all categories
    categories = session.exec(
        select(Tag)
        .where(Tag.is_category == True)
        .order_by(Tag.sort_order, Tag.name)
    ).all()

    result = []
    for category in categories:
        # 2. Get child tags for this category
        children_query = (
            select(Tag, func.count(TagLinkAssociation.link_id).label("count"))
            .outerjoin(TagLinkAssociation)
            .where(Tag.parent_id == category.id)
            .group_by(Tag.id)
            .order_by(func.count(TagLinkAssociation.link_id).desc())
        )
        children_results = session.exec(children_query).all()

        child_tags = [
            TagWithCount(
                id=tag.id,
                name=tag.name,
                color=tag.color,
                parent_id=tag.parent_id,
                is_category=False,
                count=count,
            )
            for tag, count in children_results
        ]

        # 3. Calculate total count for category
        total_count = sum(t.count for t in child_tags)

        result.append(CategoryWithTags(
            id=category.id,
            name=category.name,
            color=category.color,
            count=total_count,
            tags=child_tags,
        ))

    # Sort by total count descending
    result.sort(key=lambda x: x.count, reverse=True)

    return result


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, session: Session = Depends(get_session)):
    """Get a single tag by ID"""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagResponse(id=tag.id, name=tag.name, color=tag.color)


@router.post("", response_model=TagResponse, status_code=201)
def create_tag(
    tag_data: TagCreate,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Create a new tag. Requires authentication."""
    # Check if tag already exists
    existing = session.exec(select(Tag).where(Tag.name == tag_data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")

    tag = Tag(name=tag_data.name, color=tag_data.color)
    session.add(tag)
    session.commit()
    session.refresh(tag)

    return TagResponse(id=tag.id, name=tag.name, color=tag.color)


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_data: TagCreate,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Update a tag. Requires authentication."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if new name conflicts with existing tag
    if tag_data.name != tag.name:
        existing = session.exec(select(Tag).where(Tag.name == tag_data.name)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tag name already exists")

    tag.name = tag_data.name
    tag.color = tag_data.color

    session.add(tag)
    session.commit()
    session.refresh(tag)

    return TagResponse(id=tag.id, name=tag.name, color=tag.color)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    session: Session = Depends(get_session),
    _: str = Depends(require_auth),
):
    """Delete a tag. Requires authentication."""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()
