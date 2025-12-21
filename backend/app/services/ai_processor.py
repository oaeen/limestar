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


@dataclass
class CandidateResult:
    """First stage result with candidate tags"""

    title: str
    description: str
    candidate_categories: List[str]  # 1-2 candidate categories
    candidate_tags: List[str]  # 5-8 candidate tags


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
        Legacy single-stage process (kept for compatibility).
        Now delegates to two-stage processing.
        """
        return await self.process_two_stage(
            url=url,
            title=title,
            content=content,
            user_note=user_note,
            existing_tags=existing_tags,
            existing_categories=existing_categories,
        )

    async def process_two_stage(
        self,
        url: str,
        title: Optional[str],
        content: str,
        user_note: Optional[str] = None,
        existing_tags: Optional[List[str]] = None,
        existing_categories: Optional[List[str]] = None,
    ) -> ProcessResult:
        """
        Two-stage processing: generate candidates first, then filter and classify.

        Stage 1: Generate candidate tags freely (without reference to existing tags)
        Stage 2: Filter and merge with existing tags, determine final category
        """
        try:
            # Stage 1: Generate candidates
            candidates = await self._generate_candidates(url, title, content, user_note)

            # Stage 2: Filter and classify
            result = await self._filter_and_classify(
                candidates=candidates,
                existing_tags=existing_tags or [],
                existing_categories=existing_categories or [],
            )
            return result

        except Exception as e:
            print(f"Two-stage AI processing error: {e}")
            return ProcessResult(
                title=title or "未知标题",
                description=user_note or "",
                category="未分类",
                tags=[],
            )

    async def _generate_candidates(
        self,
        url: str,
        title: Optional[str],
        content: str,
        user_note: Optional[str] = None,
    ) -> CandidateResult:
        """Stage 1: Generate candidate tags and categories freely"""

        prompt = f"""你是一个技术内容分析专家。请分析以下网页内容，生成中文标题、介绍，以及多个候选分类和标签。

URL: {url}
原标题: {title or '无'}
{f"用户备注: {user_note}" if user_note else ""}

网页内容摘要:
{content[:3000]}

请返回 JSON 格式：
{{
    "title": "简洁的中文标题",
    "description": "2-3句话的中文介绍",
    "candidate_categories": ["候选分类1", "候选分类2"],
    "candidate_tags": ["标签1", "标签2", "标签3", "标签4", "标签5", "标签6"]
}}

要求：
1. 标题简洁明了，不超过30字。如果原标题是中文且合适可直接使用
2. 介绍控制在120字以内，突出内容价值，不要换行
3. 候选分类（1-2个）：
   - 准确描述内容所属的技术领域
   - 常见分类示例：前端开发、后端开发、大模型应用、DevOps、移动开发、数据科学、系统架构、效率工具、编程语言、云计算、安全技术、产品设计、开源项目等
   - 根据内容主题选择最贴切的分类，不要强行归类
4. 候选标签（5-8个）：
   - 尽可能多地提取相关标签
   - 包括：具体技术、框架、产品名称、方法论、概念等
   - 专业术语保留英文（如 React, Vue, LLM, Agent, Claude, GPT, MCP, RAG, Kubernetes, Docker 等）
   - 中文概念用中文（如 Prompt工程, 微服务, 状态管理 等）
   - 标签要具体，避免过于宽泛的词（如"开发"、"工具"、"教程"）
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的技术内容分析专家，擅长分析网页内容并提取关键信息。始终返回有效的 JSON 格式。",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=600,
        )

        result = json.loads(response.choices[0].message.content)

        return CandidateResult(
            title=result.get("title", title or "未知标题"),
            description=result.get("description", ""),
            candidate_categories=result.get("candidate_categories", ["未分类"])[:2],
            candidate_tags=result.get("candidate_tags", [])[:8],
        )

    async def _filter_and_classify(
        self,
        candidates: CandidateResult,
        existing_tags: List[str],
        existing_categories: List[str],
    ) -> ProcessResult:
        """Stage 2: Filter candidates and merge with existing tags"""

        # Build context for existing data
        categories_context = ""
        if existing_categories:
            categories_context = f"现有分类库: {', '.join(existing_categories)}"

        tags_context = ""
        if existing_tags:
            tags_context = f"现有标签库: {', '.join(existing_tags[:50])}"

        prompt = f"""你是一个标签管理专家。请根据候选标签和现有标签库，确定最终的分类和标签。

候选分类: {', '.join(candidates.candidate_categories)}
候选标签: {', '.join(candidates.candidate_tags)}

{categories_context}
{tags_context}

请返回 JSON 格式：
{{
    "category": "最终分类",
    "tags": ["标签1", "标签2", "标签3", "标签4"]
}}

要求：
1. 最终分类：
   - 如果候选分类与现有分类语义相同或非常接近，选择现有分类（如"前端"和"前端开发"应选择已有的那个）
   - 如果候选分类是全新的领域，可以创建新分类
   - 不要把不相关的内容强行归到已有分类

2. 最终标签（3-4个）：
   - 从候选标签中选择最有代表性的
   - 如果候选标签与现有标签语义相同，优先使用现有标签（保持一致性）
   - 合并相似标签（如 "Prompt Engineering" 和 "Prompt工程" 选择一个）
   - 确保标签与分类不重复
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个标签管理专家，擅长整理和归类标签。始终返回有效的 JSON 格式。",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for more consistent classification
            max_tokens=300,
        )

        result = json.loads(response.choices[0].message.content)

        return ProcessResult(
            title=candidates.title,
            description=candidates.description,
            category=result.get("category", candidates.candidate_categories[0] if candidates.candidate_categories else "未分类"),
            tags=result.get("tags", candidates.candidate_tags[:4])[:4],
        )


# Global instance
ai_processor = AIProcessor()
