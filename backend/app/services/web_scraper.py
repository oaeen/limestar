"""Web Scraper Service - Fetch and extract content from URLs"""

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from readability import Document


@dataclass
class ScrapedContent:
    """Scraped web page content"""

    url: str
    title: Optional[str]
    text_content: str
    favicon_url: Optional[str]
    og_image_url: Optional[str]
    og_description: Optional[str]


class WebScraper:
    """Web scraper for fetching and extracting page content"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    async def fetch(self, url: str) -> ScrapedContent:
        """Fetch and extract content from a URL"""
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers=self.headers,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")

        # Extract readable content using readability
        doc = Document(html)
        title = doc.title() or self._get_title(soup)
        content = BeautifulSoup(doc.summary(), "html.parser").get_text(
            separator=" ", strip=True
        )

        # Limit content length
        content = content[:5000] if content else ""

        # Extract metadata
        favicon_url = self._get_favicon(soup, url)
        og_image_url = self._get_og_image(soup)
        og_description = self._get_og_description(soup)

        return ScrapedContent(
            url=url,
            title=title,
            text_content=content,
            favicon_url=favicon_url,
            og_image_url=og_image_url,
            og_description=og_description,
        )

    def _get_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title"""
        # Try og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]

        # Fall back to <title> tag
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        return None

    def _get_favicon(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract favicon URL"""
        # Try various favicon link types
        for rel in ["icon", "shortcut icon", "apple-touch-icon"]:
            link = soup.find("link", rel=lambda x: x and rel in x.lower() if x else False)
            if link and link.get("href"):
                return urljoin(base_url, link["href"])

        # Default to /favicon.ico
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

    def _get_og_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract Open Graph image"""
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]

        # Try twitter:image
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return twitter_image["content"]

        return None

    def _get_og_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract Open Graph description"""
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"]

        # Try meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]

        return None


# Global instance
web_scraper = WebScraper()
