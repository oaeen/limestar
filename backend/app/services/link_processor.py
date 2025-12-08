"""Link Processor Service - Orchestrates web scraping and AI processing"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select

from app.models import Link, Tag, TagLinkAssociation
from app.services.web_scraper import web_scraper
from app.services.ai_processor import ai_processor


class LinkProcessor:
    """Orchestrates the full link processing pipeline"""

    async def process_link(
        self,
        link_id: int,
        session: Session,
    ) -> Link:
        """
        Process a link: fetch content, generate AI summary, and update tags.

        Args:
            link_id: ID of the link to process
            session: Database session

        Returns:
            Updated Link object
        """
        # Get link
        link = session.get(Link, link_id)
        if not link:
            raise ValueError(f"Link {link_id} not found")

        if link.is_processed:
            return link

        try:
            # 1. Fetch web content
            scraped = await web_scraper.fetch(link.url)

            # 2. Get existing tags for reference
            existing_tags = self._get_existing_tags(session)

            # 3. AI processing
            result = await ai_processor.process(
                url=link.url,
                title=scraped.title,
                content=scraped.text_content,
                user_note=link.user_note,
                existing_tags=existing_tags,
            )

            # 4. Update link
            link.title = result.title
            link.description = result.description
            link.favicon_url = scraped.favicon_url
            link.og_image_url = scraped.og_image_url
            link.is_processed = True
            link.updated_at = datetime.utcnow()

            # 5. Handle tags
            self._update_link_tags(link, result.tags, session)

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

    def _get_existing_tags(self, session: Session) -> List[str]:
        """Get list of existing tag names"""
        tags = session.exec(select(Tag)).all()
        return [tag.name for tag in tags]

    def _update_link_tags(
        self,
        link: Link,
        tag_names: List[str],
        session: Session,
    ) -> None:
        """Update link's tags, creating new tags if needed"""
        # Clear existing tags
        link.tags = []

        for tag_name in tag_names:
            # Find or create tag
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()  # Get the ID

            link.tags.append(tag)


# Global instance
link_processor = LinkProcessor()
