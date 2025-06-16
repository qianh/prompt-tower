from urllib.parse import quote
from typing import List, Dict, Any, Optional
from backend.config import settings
import logging
import httpx

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        if settings.USE_DATABASE:
            from backend.services.db_service import DatabaseService
            self.storage_service = DatabaseService()
        else:
            from backend.services.file_service import FileService
            self.storage_service = FileService()

    async def search_prompts(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """MCP搜索接口"""
        query = params.get("query", "")
        search_in = params.get("search_in", ["title", "tags", "content"])
        limit = params.get("limit", 20)

        logger.info(
            f"Searching prompts: query='{query}', search_in={search_in}, limit={limit}"
        )

        # 只搜索启用的prompts
        all_prompts = await self.storage_service.search_prompts(query, search_in)
        enabled_prompts = [p for p in all_prompts if p.status == "enabled"]

        # 转换为MCP格式
        results = []
        for prompt in enabled_prompts[:limit]:
            results.append(
                {
                    "title": prompt.title,
                    "content": prompt.content,
                    "tags": prompt.tags,
                    "remark": prompt.remark,
                    "score": self._calculate_score(prompt, query, search_in),
                }
            )

        logger.info(f"Found {len(results)} prompts")
        return results

    def _calculate_score(self, prompt, query: str, search_in: List[str]) -> int:
        """计算搜索得分"""
        score = 0
        query_lower = query.lower()

        if "title" in search_in and query_lower in prompt.title.lower():
            score = 100
        elif "tags" in search_in:
            for tag in prompt.tags:
                if query_lower in tag.lower():
                    score = max(score, 50)
        elif "content" in search_in and query_lower in prompt.content.lower():
            score = max(score, 10)

        return score

    async def get_prompt_names(self, params: Dict[str, Any]) -> List[str]:
        """获取所有可用的prompt名称"""
        all_prompts = await self.storage_service.list_prompts()
        enabled_prompts = [p for p in all_prompts if p.status == "enabled"]
        names = [p.title for p in enabled_prompts]
        logger.info(f"Returning {len(names)} prompt names")
        return names

    async def get_prompt(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """根据标题获取prompt"""
        title = params.get("title")
        if not title:
            raise ValueError("Title is required")

        prompt = await self.storage_service.read_prompt(title)
        if not prompt or prompt.status != "enabled":
            return None

        # Increment usage count by calling the backend API
        try:
            async with httpx.AsyncClient() as client:
                prompt_title_encoded = quote(prompt.title)
                increment_url = f"http://localhost:8010/api/v1/prompts/{prompt_title_encoded}/increment-usage"
                response = await client.post(increment_url)
                response.raise_for_status()  # Raise an exception for bad status codes
                logger.info(f"Successfully incremented usage count for prompt: {prompt.title}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error incrementing usage count for prompt {prompt.title} (HTTP {e.response.status_code}): {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Request error while incrementing usage count for prompt {prompt.title}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error incrementing usage count for prompt {prompt.title}: {str(e)}")

        return {
            "title": prompt.title,
            "content": prompt.content,
            "tags": prompt.tags,
            "remark": prompt.remark,
            "created_at": prompt.created_at.isoformat(),
            "updated_at": prompt.updated_at.isoformat(),
        }

    async def list_prompts(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """列出所有prompts"""
        tags_filter = params.get("tags", [])

        all_prompts = await self.storage_service.list_prompts()
        enabled_prompts = [p for p in all_prompts if p.status == "enabled"]

        # 按标签过滤
        if tags_filter:
            enabled_prompts = [
                p for p in enabled_prompts if any(tag in p.tags for tag in tags_filter)
            ]

        # 转换格式
        results = []
        for prompt in enabled_prompts:
            results.append(
                {
                    "title": prompt.title,
                    "content": prompt.content,
                    "tags": prompt.tags,
                    "remark": prompt.remark,
                }
            )

        return results
