"""Link Processor Service - Orchestrates web scraping and AI processing"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select

from app.models import Link, Tag, TagLinkAssociation
from app.services.web_scraper import web_scraper
from app.services.ai_processor import ai_processor


class LinkProcessor:
    """Orchestrates the full link processing pipeline"""

    def _normalize_url(self, url: str) -> str:
        """规范化URL，确保有协议前缀"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

    async def process_link(
        self,
        link_id: int,
        session: Session,
        hint: Optional[str] = None,
        force: bool = False,
    ) -> Link:
        """
        Process a link: fetch content, generate AI summary, and update tags.

        Args:
            link_id: ID of the link to process
            session: Database session
            hint: Optional hint to guide AI tag generation
            force: Force reprocess even if already processed

        Returns:
            Updated Link object
        """
        # Get link
        link = session.get(Link, link_id)
        if not link:
            raise ValueError(f"Link {link_id} not found")

        if link.is_processed and not force:
            return link

        try:
            # 1. Fetch web content
            scraped = await web_scraper.fetch(link.url)

            # 2. Get existing tags and categories for reference
            existing_tags = self._get_existing_tags(session)
            existing_categories = self._get_existing_categories(session)

            # 3. AI processing
            result = await ai_processor.process_two_stage(
                url=link.url,
                title=scraped.title,
                content=scraped.text_content,
                user_note=link.user_note,
                existing_tags=existing_tags,
                existing_categories=existing_categories,
                hint=hint,
            )

            # 4. Update link
            link.title = result.title
            link.description = result.description
            link.favicon_url = scraped.favicon_url
            link.og_image_url = scraped.og_image_url
            link.is_processed = True
            link.updated_at = datetime.utcnow()

            # 5. Handle tags (category + sub-tags)
            self._update_link_tags(link, result.category, result.tags, session)

            session.add(link)
            session.commit()
            session.refresh(link)

            return link

        except Exception as e:
            print(f"Error processing link {link_id}: {e}")
            # Mark as processed to avoid retrying failed links
            link.is_processed = True
            link.description = f"处理失败: {str(e)}"
            session.add(link)
            session.commit()
            raise

    async def add_and_process_link(
        self,
        url: str,
        user_note: Optional[str],
        session: Session,
        submitted_by: Optional[str] = None,
    ) -> Link:
        """
        Add a new link and process it immediately.

        Args:
            url: URL to add
            user_note: Optional user note
            session: Database session
            submitted_by: Optional submitter identifier

        Returns:
            Processed Link object
        """
        from urllib.parse import urlparse

        # Normalize URL (add https:// if missing)
        url = self._normalize_url(url)

        # Extract domain
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split("/")[0]

        # Check if URL already exists
        existing = session.exec(select(Link).where(Link.url == url)).first()
        if existing:
            return existing

        # Create link
        link = Link(
            url=url,
            title=domain,  # Temporary title
            description="",
            user_note=user_note,
            domain=domain,
            submitted_by=submitted_by,
            is_processed=False,
        )

        session.add(link)
        session.commit()
        session.refresh(link)

        # Process the link
        return await self.process_link(link.id, session)

    def _get_existing_categories(self, session: Session) -> List[str]:
        """Get list of existing category names"""
        categories = session.exec(
            select(Tag).where(Tag.is_category == True)
        ).all()
        return [cat.name for cat in categories]

    def _get_existing_tags(self, session: Session) -> List[str]:
        """Get list of existing sub-tag names"""
        tags = session.exec(
            select(Tag).where(Tag.is_category == False)
        ).all()
        return [tag.name for tag in tags]

    def _update_link_tags(
        self,
        link: Link,
        category_name: str,
        tag_names: List[str],
        session: Session,
    ) -> None:
        """Update link's tags with hierarchical structure (category + sub-tags)"""
        # Clear existing tags
        link.tags = []

        # 1. Find or create category
        category = session.exec(
            select(Tag).where(Tag.name == category_name, Tag.is_category == True)
        ).first()

        if not category:
            # Create new category with a distinct color
            category = Tag(
                name=category_name,
                is_category=True,
                parent_id=None,
                color=self._generate_category_color(session),
            )
            session.add(category)
            session.flush()

        link.tags.append(category)

        # 2. Add sub-tags under this category
        for tag_name in tag_names:
            # Find existing sub-tag under this category
            tag = session.exec(
                select(Tag).where(
                    Tag.name == tag_name,
                    Tag.parent_id == category.id,
                    Tag.is_category == False
                )
            ).first()

            if not tag:
                # Create new sub-tag
                tag = Tag(
                    name=tag_name,
                    parent_id=category.id,
                    is_category=False,
                    color=category.color,  # Inherit category color
                )
                session.add(tag)
                session.flush()

            link.tags.append(tag)

    def _generate_category_color(self, session: Session) -> str:
        """Generate a color for new category based on existing count"""
        colors = [
            "#8B5CF6",  # Purple
            "#06B6D4",  # Cyan
            "#3B82F6",  # Blue
            "#10B981",  # Green
            "#F59E0B",  # Orange
            "#EC4899",  # Pink
            "#6B7280",  # Gray
            "#EF4444",  # Red
            "#14B8A6",  # Teal
            "#F97316",  # Deep Orange
        ]
        category_count = session.exec(
            select(Tag).where(Tag.is_category == True)
        ).all()
        return colors[len(category_count) % len(colors)]


# Global instance
link_processor = LinkProcessor()
