"""AI Processor Service - Generate Chinese summaries and auto-tag links"""

import json
from dataclasses import dataclass
from typing import List, Optional
from openai import AsyncOpenAI

from app.config import settings


@dataclass
class ProcessResult:
    """AI processing result"""

    title: str
    description: str
    tags: List[str]


class AIProcessor:
    """AI processor for generating summaries and tags"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.OPENAI_MODEL_NAME

    async def process(
        self,
        url: str,
        title: Optional[str],
        content: str,
        user_note: Optional[str] = None,
        existing_tags: Optional[List[str]] = None,
    ) -> ProcessResult:
        """
        Process a link and generate Chinese summary and tags.

        Args:
            url: The URL of the link
            title: Original page title
            content: Extracted page content
            user_note: User provided note/description
            existing_tags: List of existing tags in the system for reference

        Returns:
            ProcessResult with title, description, and tags
        """
        # Build prompt
        tags_hint = ""
        if existing_tags:
            tags_hint = f"\n现有标签供参考（优先使用这些标签）: {', '.join(existing_tags[:20])}"

        prompt = f"""你是一个链接收藏助手。请分析以下网页内容，生成简洁的中文介绍和相关标签。

URL: {url}
原标题: {title or '无'}
{f"用户备注: {user_note}" if user_note else ""}

网页内容摘要:
{content[:3000]}
{tags_hint}

请返回 JSON 格式：
{{
    "title": "简洁的中文标题（如果原标题是中文且合适可直接使用，否则翻译或重新拟定）",
    "description": "2-3句话的中文介绍，概括网页的主要内容和价值",
    "tags": ["标签1", "标签2", "标签3"]
}}

要求：
1. 标题简洁明了，不超过50字
2. 介绍要突出内容的价值和特点
3. 标签2-5个，使用通用的分类词（如：工具、设计、开发、AI、教程、资源等）
4. 所有内容使用中文"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的链接收藏助手，擅长分析网页内容并生成简洁的中文介绍。始终返回有效的 JSON 格式。",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500,
            )

            result = json.loads(response.choices[0].message.content)

            return ProcessResult(
                title=result.get("title", title or "未知标题"),
                description=result.get("description", ""),
                tags=result.get("tags", [])[:5],  # Limit to 5 tags
            )

        except Exception as e:
            # Fallback if AI fails
            print(f"AI processing error: {e}")
            return ProcessResult(
                title=title or "未知标题",
                description=user_note or "",
                tags=[],
            )


# Global instance
ai_processor = AIProcessor()
