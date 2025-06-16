from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from backend.config import settings
from backend.models import Prompt, PromptCreate, PromptUpdate
from backend.utils.validators import (validate_content, validate_tags,
                                      validate_title)


class PromptService:
    """Prompt业务逻辑服务"""

    def __init__(self):
        if settings.USE_DATABASE:
            from backend.services.db_service import DatabaseService
            self.storage_service = DatabaseService()
        else:
            from backend.services.file_service import FileService
            self.storage_service = FileService()
        
        # 导入标签服务
        from backend.services.unified_tag_service import tag_service
        self.tag_service = tag_service

    async def create_prompt(
        self, prompt_data: PromptCreate, creator_username: str
    ) -> Prompt:
        """创建新的prompt，并将其中的tags同步到全局tags.json"""
        # 验证数据
        if not validate_title(prompt_data.title):
            raise ValueError("标题格式不正确")

        if not validate_content(prompt_data.content):
            raise ValueError("内容不能为空或超过长度限制")

        if prompt_data.tags and not validate_tags(prompt_data.tags):
            raise ValueError("标签格式不正确")

        # 检查标题是否已存在
        existing = await self.storage_service.read_prompt(prompt_data.title)
        if existing:
            raise ValueError(f"标题 '{prompt_data.title}' 已存在")

        # 保存prompt
        data_to_save = prompt_data.model_dump()
        data_to_save["creator_username"] = creator_username
        saved_prompt = await self.storage_service.save_prompt(data_to_save)

        # 同步tags到全局标签系统
        if saved_prompt and saved_prompt.tags:
            for tag in saved_prompt.tags:
                try:
                    await self.tag_service.add_tag(tag)
                except ValueError as e:
                    # Log or handle tag validation error if necessary, e.g., empty tag from prompt
                    print(f"Skipping invalid tag '{tag}' from prompt '{saved_prompt.title}': {e}")
                except Exception as e:
                    print(f"Error adding tag '{tag}' for prompt '{saved_prompt.title}' to global list: {e}")
        
        return saved_prompt

    async def update_prompt(
        self, title: str, update_data: PromptUpdate, current_username: str
    ) -> Optional[Prompt]:
        """更新prompt，并将其中的tags同步到全局tags.json"""
        # 获取原始prompt
        original_prompt = await self.storage_service.read_prompt(title)
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

        updated_prompt = await self.storage_service.update_prompt(title, update_dict)

        # 同步tags到全局标签系统
        if updated_prompt and updated_prompt.tags:
            for tag in updated_prompt.tags:
                try:
                    await self.tag_service.add_tag(tag)
                except ValueError as e:
                    print(f"Skipping invalid tag '{tag}' from prompt '{updated_prompt.title}': {e}")
                except Exception as e:
                    print(f"Error adding tag '{tag}' for prompt '{updated_prompt.title}' to global list: {e}")

        return updated_prompt

    async def delete_prompt(self, title: str, current_username: str) -> bool:
        """删除prompt，校验操作者是否为创建者"""
        original_prompt = await self.storage_service.read_prompt(title)
        if not original_prompt:
            raise HTTPException(status_code=404, detail="Prompt不存在")

        if original_prompt.creator_username != current_username:
            raise HTTPException(status_code=403, detail="无权限删除此Prompt")

        return await self.storage_service.delete_prompt(title)

    async def toggle_prompt_status(
        self, title: str, current_username: str
    ) -> Optional[Prompt]:
        """切换prompt状态，校验操作者是否为创建者"""
        original_prompt = await self.storage_service.read_prompt(title)
        if not original_prompt:
            raise HTTPException(status_code=404, detail="Prompt不存在")

        if original_prompt.creator_username != current_username:
            raise HTTPException(status_code=403, detail="无权限修改此Prompt的状态")

        new_status = "disabled" if original_prompt.status == "enabled" else "enabled"
        return await self.storage_service.update_prompt(title, {"status": new_status})

    async def get_enabled_prompts(self) -> List[Prompt]:
        """获取所有启用的prompts"""
        all_prompts = await self.storage_service.list_prompts()
        return [p for p in all_prompts if p.status == "enabled"]

    async def get_all_tags_from_yaml_files(self) -> List[str]:
        """获取所有不重复的tags (从YAML文件，用于初始同步)
           This method is intended to be called at application startup.
        """
        all_prompts = await self.storage_service.list_prompts()
        all_tags = set()
        for prompt in all_prompts:
            if prompt.tags:
                for tag_from_yaml in prompt.tags:
                    if isinstance(tag_from_yaml, str) and tag_from_yaml.strip(): # Ensure it is a valid string tag
                        all_tags.add(tag_from_yaml.strip())
        return sorted(list(all_tags))

    async def increment_usage_count(self, title: str) -> Optional[Prompt]:
        """增加指定prompt的使用次数"""
        prompt = await self.storage_service.read_prompt(title)
        if not prompt:
            # No need to raise HTTPException here if called internally, 
            # but good if this service method could also be called directly from API in future.
            # For now, let's assume API layer handles 404 if needed.
            # Consider returning None or letting file_service.update_prompt handle it.
            return None 

        new_usage_count = prompt.usage_count + 1
        # We need to ensure that update_prompt can handle just updating usage_count
        # and that it correctly identifies the prompt by its title (which is the identifier here)
        updated_prompt = await self.storage_service.update_prompt(
            original_title_identifier=title, 
            update_data={"usage_count": new_usage_count}
        )
        return updated_prompt


async def get_prompt_by_username_count(username: str) -> int:
    """获取指定用户创建的提示词数量"""
    try:
        from backend.config import settings
        
        if settings.USE_DATABASE:
            from backend.services.db_service import DatabaseService
            storage_service = DatabaseService()
            return await storage_service.get_prompt_count_by_username(username)
        else:
            from backend.services.file_service import FileService
            file_service = FileService()
            prompts = await file_service.list_prompts()
            
            # 安全计数
            count = 0
            for prompt in prompts:
                if hasattr(prompt, 'creator_username') and prompt.creator_username == username:
                    count += 1
            
            return count
    except Exception as e:
        print(f"ERROR calculating prompt count for user '{username}': {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        return 0
