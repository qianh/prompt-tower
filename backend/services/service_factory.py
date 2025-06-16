"""
服务工厂 - 根据配置选择使用文件服务还是数据库服务
"""
from typing import Protocol, List, Optional, Dict, Any

from backend.config import settings
from backend.models import Prompt, PromptCreate, PromptUpdate, UserCreate, UserInDB


class PromptServiceProtocol(Protocol):
    """提示词服务协议"""
    async def list_prompts(self) -> List[Prompt]: ...
    async def read_prompt(self, title: str) -> Optional[Prompt]: ...
    async def save_prompt(self, prompt_data: Dict[str, Any]) -> Prompt: ...
    async def update_prompt(self, title: str, update_data: Dict[str, Any]) -> Optional[Prompt]: ...
    async def delete_prompt(self, title: str) -> bool: ...
    async def search_prompts(self, query: str, search_in: List[str]) -> List[Prompt]: ...


class UserServiceProtocol(Protocol):
    """用户服务协议"""
    async def get_user_by_username(self, username: str) -> Optional[UserInDB]: ...
    async def create_user(self, user_data: UserCreate, hashed_password: str) -> Optional[UserInDB]: ...
    async def get_all_users(self) -> List[UserInDB]: ...


class TagServiceProtocol(Protocol):
    """标签服务协议"""
    async def get_all_tags(self) -> List[str]: ...
    async def add_tag(self, tag_name: str) -> str: ...


def get_prompt_service() -> PromptServiceProtocol:
    """获取提示词服务实例"""
    if settings.USE_DATABASE:
        from backend.services.db_service import DatabaseService
        return DatabaseService()
    else:
        from backend.services.file_service import FileService
        return FileService()


def get_user_service() -> UserServiceProtocol:
    """获取用户服务实例"""
    if settings.USE_DATABASE:
        from backend.services.db_service import DatabaseService
        return DatabaseService()
    else:
        from backend.services import user_service
        return user_service


def get_tag_service() -> TagServiceProtocol:
    """获取标签服务实例"""
    if settings.USE_DATABASE:
        from backend.services.db_service import DatabaseService
        return DatabaseService()
    else:
        from backend.services import tag_service
        return tag_service