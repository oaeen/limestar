"""LimeStar Database Models"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class TagLinkAssociation(SQLModel, table=True):
    """Many-to-many association between Tag and Link"""

    __tablename__ = "tag_link_association"

    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    link_id: int = Field(foreign_key="link.id", primary_key=True)


class Tag(SQLModel, table=True):
    """Tag model for categorizing links with hierarchical structure"""

    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=50)
    color: str = Field(default="#007AFF", max_length=7)  # Apple Blue default

    # Hierarchical fields
    parent_id: Optional[int] = Field(default=None, foreign_key="tag.id", index=True)
    is_category: bool = Field(default=False)  # True = category, False = sub-tag
    sort_order: int = Field(default=0)  # Sorting weight

    # Relationships
    links: List["Link"] = Relationship(
        back_populates="tags", link_model=TagLinkAssociation
    )


class Link(SQLModel, table=True):
    """Link model for storing bookmarks"""

    __tablename__ = "link"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Core fields
    url: str = Field(index=True, max_length=2048)
    title: str = Field(max_length=500)
    description: str = Field(default="")  # AI generated Chinese description
    user_note: Optional[str] = Field(default=None)  # User provided note

    # Metadata
    favicon_url: Optional[str] = Field(default=None, max_length=2048)
    og_image_url: Optional[str] = Field(default=None, max_length=2048)
    domain: str = Field(index=True, max_length=255)  # Extracted domain

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Source tracking
    submitted_by: Optional[str] = Field(default=None, max_length=100)

    # Processing status
    is_processed: bool = Field(default=False)

    # Relationships
    tags: List[Tag] = Relationship(
        back_populates="links", link_model=TagLinkAssociation
    )
