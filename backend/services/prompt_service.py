from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from backend.services.file_service import FileService
from backend.models import Prompt, PromptCreate, PromptUpdate
from backend.utils.validators import validate_title, validate_tags, validate_content


class PromptService:
    """Prompt业务逻辑服务"""

    def __init__(self):
        self.file_service = FileService()

    async def create_prompt(
        self, prompt_data: PromptCreate, creator_username: str
    ) -> Prompt:
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
        data_to_save = prompt_data.model_dump()
        data_to_save["creator_username"] = creator_username
        return await self.file_service.save_prompt(data_to_save)

    async def update_prompt(
        self, title: str, update_data: PromptUpdate, current_username: str
    ) -> Optional[Prompt]:
        """更新prompt"""
        # 获取原始prompt
        original_prompt = await self.file_service.read_prompt(title)
        if not original_prompt:
            raise HTTPException(status_code=404, detail="Prompt不存在")

        # 检查所有权
        if original_prompt.creator_username != current_username:
            raise HTTPException(status_code=403, detail="无权限修改此Prompt")

        # 验证更新数据
        if update_data.title and not validate_title(update_data.title):
            raise ValueError("标题格式不正确")

        if update_data.content and not validate_content(update_data.content):
            raise ValueError("内容不能为空或超过长度限制")

        if update_data.tags and not validate_tags(update_data.tags):
            raise ValueError("标签格式不正确")

        update_dict = update_data.model_dump(exclude_unset=True)
        # 不允许修改creator_username
        if "creator_username" in update_dict:
            del update_dict["creator_username"]

        return await self.file_service.update_prompt(title, update_dict)

    async def delete_prompt(self, title: str, current_username: str) -> bool:
        """删除prompt，校验操作者是否为创建者"""
        original_prompt = await self.file_service.read_prompt(title)
        if not original_prompt:
            raise HTTPException(status_code=404, detail="Prompt不存在")

        if original_prompt.creator_username != current_username:
            raise HTTPException(status_code=403, detail="无权限删除此Prompt")

        return await self.file_service.delete_prompt(title)

    async def toggle_prompt_status(
        self, title: str, current_username: str
    ) -> Optional[Prompt]:
        """切换prompt状态，校验操作者是否为创建者"""
        original_prompt = await self.file_service.read_prompt(title)
        if not original_prompt:
            raise HTTPException(status_code=404, detail="Prompt不存在")

        # 仅所有者可以切换状态
        if original_prompt.creator_username != current_username:
            raise HTTPException(status_code=403, detail="无权限修改此Prompt的状态")

        new_status = "disabled" if original_prompt.status == "enabled" else "enabled"
        return await self.file_service.update_prompt(title, {"status": new_status})

    async def get_enabled_prompts(self) -> List[Prompt]:
        """获取所有启用的prompts"""
        all_prompts = await self.file_service.list_prompts()
        return [p for p in all_prompts if p.status == "enabled"]
