from typing import List, Optional, Dict, Any
from backend.services.file_service import FileService
from backend.models import Prompt, PromptCreate, PromptUpdate
from backend.utils.validators import validate_title, validate_tags, validate_content


class PromptService:
    """Prompt业务逻辑服务"""

    def __init__(self):
        self.file_service = FileService()

    async def create_prompt(self, prompt_data: PromptCreate) -> Prompt:
        """创建新的prompt"""
        # 验证数据
        if not validate_title(prompt_data.title):
            raise ValueError("标题格式不正确")

        if not validate_content(prompt_data.content):
            raise ValueError("内容不能为空或超过长度限制")

        if prompt_data.tags and not validate_tags(prompt_data.tags):
            raise ValueError("标签格式不正确")

        # 检查标题是否已存在
        existing = await self.file_service.read_prompt(prompt_data.title)
        if existing:
            raise ValueError(f"标题 '{prompt_data.title}' 已存在")

        # 保存prompt
        return await self.file_service.save_prompt(prompt_data.model_dump())

    async def update_prompt(
        self, title: str, update_data: PromptUpdate
    ) -> Optional[Prompt]:
        """更新prompt"""
        # 验证更新数据
        if update_data.title and not validate_title(update_data.title):
            raise ValueError("标题格式不正确")

        if update_data.content and not validate_content(update_data.content):
            raise ValueError("内容不能为空或超过长度限制")

        if update_data.tags and not validate_tags(update_data.tags):
            raise ValueError("标签格式不正确")

        return await self.file_service.update_prompt(
            title, update_data.model_dump(exclude_unset=True)
        )

    async def get_enabled_prompts(self) -> List[Prompt]:
        """获取所有启用的prompts"""
        all_prompts = await self.file_service.list_prompts()
        return [p for p in all_prompts if p.status == "enabled"]
