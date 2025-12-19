"""AI Processor Service - Generate Chinese summaries and auto-tag links"""

import json
from dataclasses import dataclass
from typing import List, Optional
from openai import AsyncOpenAI

from app.config import settings


@dataclass
class ProcessResult:
    """AI processing result with hierarchical tags"""

    title: str
    description: str
    category: str  # Main category name
    tags: List[str]  # Sub-tags


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
        existing_categories: Optional[List[str]] = None,
    ) -> ProcessResult:
        """
        Process a link and generate Chinese summary and hierarchical tags.

        Args:
            url: The URL of the link
            title: Original page title
            content: Extracted page content
            user_note: User provided note/description
            existing_tags: List of existing sub-tags in the system for reference
            existing_categories: List of existing categories for reference

        Returns:
            ProcessResult with title, description, category and tags
        """
        # Build hints for existing data
        categories_hint = ""
        if existing_categories:
            categories_hint = f"\n现有主分类（优先复用）: {', '.join(existing_categories)}"

        tags_hint = ""
        if existing_tags:
            tags_hint = f"\n现有子标签供参考（优先复用）: {', '.join(existing_tags[:30])}"

        prompt = f"""你是一个技术链接收藏助手。请分析以下网页内容，生成简洁的中文介绍，并分配一个主分类和精准的子标签。

URL: {url}
原标题: {title or '无'}
{f"用户备注: {user_note}" if user_note else ""}

网页内容摘要:
{content[:3000]}
{categories_hint}
{tags_hint}

请返回 JSON 格式：
{{
    "title": "简洁的中文标题（如果原标题是中文且合适可直接使用，否则翻译或重新拟定）",
    "description": "2-3句话的中文介绍，概括网页的主要内容和价值",
    "category": "主分类名称",
    "tags": ["子标签1", "子标签2", "子标签3"]
}}

要求：
1. 标题简洁明了，不超过30字
2. 介绍必须控制在120字以内，突出内容的价值和特点，不要换行
3. 主分类要求：
   - 描述内容所属的技术领域或方向（如"大模型应用"、"前端开发"、"效率工具"、"编程语言"等）
   - 如果现有主分类匹配，必须复用，不要创建语义相近的新分类
   - 主分类应具有聚合价值，避免过于具体或过于宽泛
4. 子标签要求：
   - 1-4个子标签，描述具体的技术、产品、框架或方法
   - 专业术语保留英文（如 LLM, Agent, Claude, GPT, MCP, RAG, Prompt Engineering, Next.js, React 等）
   - 子标签不要重复主分类的含义
   - 避免使用过于宽泛的词如"AI"、"开发"、"工具"、"教程"
"""

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
                category=result.get("category", "未分类"),
                tags=result.get("tags", [])[:4],  # Limit to 4 sub-tags
            )

        except Exception as e:
            # Fallback if AI fails
            print(f"AI processing error: {e}")
            return ProcessResult(
                title=title or "未知标题",
                description=user_note or "",
                category="未分类",
                tags=[],
            )


# Global instance
ai_processor = AIProcessor()
