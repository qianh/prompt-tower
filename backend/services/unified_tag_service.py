"""
统一标签服务 - 根据配置选择文件或数据库存储
"""
from typing import List

from backend.config import settings


class UnifiedTagService:
    """统一标签服务"""
    
    def __init__(self):
        if settings.USE_DATABASE:
            from backend.services.db_service import DatabaseService
            self._service = DatabaseService()
        else:
            from backend.services import tag_service as file_tag_service
            self._service = file_tag_service
    
    async def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        return await self._service.get_all_tags()
    
    async def add_tag(self, tag_name: str) -> str:
        """添加标签"""
        return await self._service.add_tag(tag_name)
    
    async def sync_tags_from_prompts(self) -> List[str]:
        """从提示词同步标签"""
        if settings.USE_DATABASE:
            # 数据库模式下，标签会在创建提示词时自动同步
            return await self._service.get_all_tags()
        else:
            return await self._service.sync_tags_from_prompts()


# 创建全局实例
tag_service = UnifiedTagService()