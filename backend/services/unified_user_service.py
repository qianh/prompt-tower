"""
统一用户服务 - 根据配置选择文件或数据库存储
"""
from typing import List, Optional

from backend.config import settings
from backend.models import UserCreate, UserInDB
from backend.utils.security import get_password_hash


class UnifiedUserService:
    """统一用户服务"""
    
    def __init__(self):
        if settings.USE_DATABASE:
            from backend.services.db_service import DatabaseService
            self._service = DatabaseService()
        else:
            from backend.services import user_service as file_user_service
            self._service = file_user_service
    
    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """根据用户名获取用户"""
        if settings.USE_DATABASE:
            return await self._service.get_user_by_username(username)
        else:
            return await self._service.get_user_by_username(username)
    
    async def create_user(self, user_data: UserCreate) -> Optional[UserInDB]:
        """创建用户"""
        if settings.USE_DATABASE:
            hashed_password = get_password_hash(user_data.password)
            return await self._service.create_user(user_data, hashed_password)
        else:
            return await self._service.create_user_in_db(user_data)
    
    async def get_all_users(self) -> List[UserInDB]:
        """获取所有用户"""
        return await self._service.get_all_users()


# 创建全局实例
user_service = UnifiedUserService()