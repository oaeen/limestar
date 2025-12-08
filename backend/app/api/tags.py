"""Tags API Routes"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.database import get_session
from app.models import Tag, TagLinkAssociation
from app.schemas import TagCreate, TagResponse, TagWithCount

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=List[TagWithCount])
def get_tags(session: Session = Depends(get_session)):
    """Get all tags with link counts"""
    # Query tags with count
    query = (
        select(Tag, func.count(TagLinkAssociation.link_id).label("count"))
        .outerjoin(TagLinkAssociation)
        .group_by(Tag.id)
        .order_by(func.count(TagLinkAssociation.link_id).desc())
    )

    results = session.exec(query).all()

    return [
        TagWithCount(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            count=count,
        )
        for tag, count in results
    ]


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, session: Session = Depends(get_session)):
    """Get a single tag by ID"""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagResponse(id=tag.id, name=tag.name, color=tag.color)


@router.post("", response_model=TagResponse, status_code=201)
def create_tag(tag_data: TagCreate, session: Session = Depends(get_session)):
    """Create a new tag"""
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
):
    """Update a tag"""
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
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    """Delete a tag"""
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()
