"""LimeStar API Schemas (Pydantic models for request/response)"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


# ============== Tag Schemas ==============

class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#007AFF"


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True


class TagWithCount(TagResponse):
    count: int = 0


# ============== Link Schemas ==============

class LinkBase(BaseModel):
    url: str
    user_note: Optional[str] = None


class LinkCreate(LinkBase):
    """Schema for creating a new link (minimal input)"""
    pass


class LinkUpdate(BaseModel):
    """Schema for updating a link"""
    title: Optional[str] = None
    description: Optional[str] = None
    user_note: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class LinkResponse(BaseModel):
    """Schema for link response"""
    id: int
    url: str
    title: str
    description: str
    user_note: Optional[str]
    favicon_url: Optional[str]
    og_image_url: Optional[str]
    domain: str
    created_at: datetime
    updated_at: datetime
    is_processed: bool
    tags: List[TagResponse]

    class Config:
        from_attributes = True


# ============== Pagination ==============

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List
    total: int
    page: int
    page_size: int
    has_more: bool


class LinkListResponse(PaginatedResponse):
    """Paginated link list response"""
    items: List[LinkResponse]


# ============== Search ==============

class SearchQuery(BaseModel):
    """Search query parameters"""
    q: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20
