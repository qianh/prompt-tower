"""
数据库服务层 - 替代文件服务
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_, select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import get_async_session, async_engine
from backend.db_models import User as DBUser, Tag as DBTag, Prompt as DBPrompt, PromptTag
from backend.models import Prompt, PromptCreate, PromptUpdate, UserCreate, UserInDB, User


class DatabaseService:
    """数据库操作服务"""

    def __init__(self):
        pass

    # ==================== 用户相关操作 ====================
    
    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """根据用户名获取用户"""
        async with AsyncSession(bind=async_engine) as session:
            result = await session.execute(
                select(DBUser).where(DBUser.username == username)
            )
            db_user = result.scalar_one_or_none()
            if db_user:
                return UserInDB(
                    id=db_user.id,
                    username=db_user.username,
                    hashed_password=db_user.hashed_password
                )
            return None

    async def create_user(self, user_data: UserCreate, hashed_password: str) -> Optional[UserInDB]:
        """创建用户"""
        async with AsyncSession(bind=async_engine) as session:
            # 检查用户是否已存在
            existing_user = await session.execute(
                select(DBUser).where(DBUser.username == user_data.username)
            )
            if existing_user.scalar_one_or_none():
                return None

            # 创建新用户
            db_user = DBUser(
                username=user_data.username,
                hashed_password=hashed_password
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

            return UserInDB(
                id=db_user.id,
                username=db_user.username,
                hashed_password=db_user.hashed_password
            )

    async def get_all_users(self) -> List[UserInDB]:
        """获取所有用户"""
        async with AsyncSession(bind=async_engine) as session:
            result = await session.execute(select(DBUser))
            db_users = result.scalars().all()
            return [
                UserInDB(
                    id=user.id,
                    username=user.username,
                    hashed_password=user.hashed_password
                )
                for user in db_users
            ]

    # ==================== 标签相关操作 ====================

    async def get_all_tags(self) -> List[str]:
        """获取所有标签名称"""
        async with AsyncSession(bind=async_engine) as session:
            result = await session.execute(
                select(DBTag.name).order_by(func.lower(DBTag.name))
            )
            return list(result.scalars().all())

    async def add_tag(self, tag_name: str) -> str:
        """添加标签（如果不存在）"""
        stripped_tag = tag_name.strip()
        if not stripped_tag:
            raise ValueError("Tag name cannot be empty.")

        async with AsyncSession(bind=async_engine) as session:
            # 检查标签是否已存在（不区分大小写）
            result = await session.execute(
                select(DBTag).where(func.lower(DBTag.name) == stripped_tag.lower())
            )
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                return existing_tag.name

            # 创建新标签
            db_tag = DBTag(name=stripped_tag)
            session.add(db_tag)
            await session.commit()
            return stripped_tag

    async def get_or_create_tag(self, tag_name: str, session: AsyncSession) -> DBTag:
        """获取或创建标签对象（在给定的会话中）"""
        stripped_tag = tag_name.strip()
        if not stripped_tag:
            raise ValueError("Tag name cannot be empty.")

        # 检查标签是否已存在
        result = await session.execute(
            select(DBTag).where(func.lower(DBTag.name) == stripped_tag.lower())
        )
        existing_tag = result.scalar_one_or_none()
        
        if existing_tag:
            return existing_tag

        # 创建新标签
        db_tag = DBTag(name=stripped_tag)
        session.add(db_tag)
        await session.flush()  # 获取ID但不提交
        return db_tag

    # ==================== 提示词相关操作 ====================

    async def list_prompts(self) -> List[Prompt]:
        """列出所有提示词"""
        async with AsyncSession(bind=async_engine) as session:
            result = await session.execute(
                select(DBPrompt)
                .options(selectinload(DBPrompt.tags))
                .order_by(DBPrompt.updated_at.desc())
            )
            db_prompts = result.scalars().all()
            
            return [self._db_prompt_to_model(db_prompt) for db_prompt in db_prompts]

    async def read_prompt(self, title: str) -> Optional[Prompt]:
        """根据标题读取提示词"""
        async with AsyncSession(bind=async_engine) as session:
            result = await session.execute(
                select(DBPrompt)
                .options(selectinload(DBPrompt.tags))
                .where(DBPrompt.title == title)
            )
            db_prompt = result.scalar_one_or_none()
            
            if db_prompt:
                return self._db_prompt_to_model(db_prompt)
            return None

    async def save_prompt(self, prompt_data: Dict[str, Any]) -> Prompt:
        """保存新的提示词"""
        async with AsyncSession(bind=async_engine) as session:
            # 检查标题是否已存在
            existing = await session.execute(
                select(DBPrompt).where(DBPrompt.title == prompt_data["title"])
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"标题 '{prompt_data['title']}' 已存在")

            # 创建提示词
            db_prompt = DBPrompt(
                title=prompt_data["title"],
                content=prompt_data["content"],
                description=prompt_data.get("remark", ""),  # 将remark映射到description
                creator_username=prompt_data.get("creator_username"),
                status=prompt_data.get("status", "enabled"),
                usage_count=prompt_data.get("usage_count", 0),
                settings={}
            )
            session.add(db_prompt)
            await session.flush()  # 获取ID

            # 处理标签
            if prompt_data.get("tags"):
                for tag_name in prompt_data["tags"]:
                    if tag_name.strip():
                        db_tag = await self.get_or_create_tag(tag_name.strip(), session)
                        db_prompt.tags.append(db_tag)

            await session.commit()
            await session.refresh(db_prompt)
            
            # 重新加载以获取标签
            result = await session.execute(
                select(DBPrompt)
                .options(selectinload(DBPrompt.tags))
                .where(DBPrompt.id == db_prompt.id)
            )
            db_prompt = result.scalar_one()
            
            return self._db_prompt_to_model(db_prompt)

    async def update_prompt(self, title: str, update_data: Dict[str, Any]) -> Optional[Prompt]:
        """更新提示词"""
        async with AsyncSession(bind=async_engine) as session:
            # 获取现有提示词
            result = await session.execute(
                select(DBPrompt)
                .options(selectinload(DBPrompt.tags))
                .where(DBPrompt.title == title)
            )
            db_prompt = result.scalar_one_or_none()
            
            if not db_prompt:
                return None

            # 如果要更新标题，检查新标题是否已存在
            new_title = update_data.get("title")
            if new_title and new_title != title:
                existing = await session.execute(
                    select(DBPrompt).where(DBPrompt.title == new_title)
                )
                if existing.scalar_one_or_none():
                    raise ValueError(f"标题 '{new_title}' 已存在")

            # 更新字段
            if "title" in update_data:
                db_prompt.title = update_data["title"]
            if "content" in update_data:
                db_prompt.content = update_data["content"]
            if "remark" in update_data:
                db_prompt.description = update_data["remark"]
            if "status" in update_data:
                db_prompt.status = update_data["status"]
            if "usage_count" in update_data:
                db_prompt.usage_count = update_data["usage_count"]

            # 处理标签更新
            if "tags" in update_data:
                # 清除现有标签关联
                db_prompt.tags.clear()
                
                # 添加新标签
                if update_data["tags"]:
                    for tag_name in update_data["tags"]:
                        if tag_name.strip():
                            db_tag = await self.get_or_create_tag(tag_name.strip(), session)
                            db_prompt.tags.append(db_tag)

            await session.commit()
            await session.refresh(db_prompt)
            
            # 重新加载以获取标签
            result = await session.execute(
                select(DBPrompt)
                .options(selectinload(DBPrompt.tags))
                .where(DBPrompt.id == db_prompt.id)
            )
            db_prompt = result.scalar_one()
            
            return self._db_prompt_to_model(db_prompt)

    async def delete_prompt(self, title: str) -> bool:
        """删除提示词"""
        async with AsyncSession(bind=async_engine) as session:
            result = await session.execute(
                select(DBPrompt).where(DBPrompt.title == title)
            )
            db_prompt = result.scalar_one_or_none()
            
            if not db_prompt:
                return False

            await session.delete(db_prompt)
            await session.commit()
            return True

    async def search_prompts(self, query: str, search_in: List[str]) -> List[Prompt]:
        """搜索提示词"""
        if not query.strip():
            return []

        async with AsyncSession(bind=async_engine) as session:
            query_lower = query.strip().lower()
            conditions = []

            # 构建搜索条件
            if "title" in search_in:
                conditions.append(func.lower(DBPrompt.title).contains(query_lower))
            if "content" in search_in:
                conditions.append(func.lower(DBPrompt.content).contains(query_lower))
            if "tags" in search_in:
                # 通过标签搜索
                tag_subquery = (
                    select(PromptTag.prompt_id)
                    .join(DBTag)
                    .where(func.lower(DBTag.name).contains(query_lower))
                )
                conditions.append(DBPrompt.id.in_(tag_subquery))

            if not conditions:
                return []

            # 执行搜索
            result = await session.execute(
                select(DBPrompt)
                .options(selectinload(DBPrompt.tags))
                .where(or_(*conditions))
                .order_by(DBPrompt.updated_at.desc())
            )
            db_prompts = result.scalars().all()

            # 计算匹配分数并排序
            scored_prompts = []
            for db_prompt in db_prompts:
                score = self._calculate_search_score(db_prompt, query_lower, search_in)
                scored_prompts.append((score, db_prompt))

            # 按分数排序
            scored_prompts.sort(key=lambda x: x[0], reverse=True)
            
            return [self._db_prompt_to_model(db_prompt) for _, db_prompt in scored_prompts]

    def _calculate_search_score(self, db_prompt: DBPrompt, query_lower: str, search_in: List[str]) -> int:
        """计算搜索匹配分数"""
        score = 0
        
        if "title" in search_in and query_lower in db_prompt.title.lower():
            score = 100
        elif "tags" in search_in:
            for tag in db_prompt.tags:
                if query_lower in tag.name.lower():
                    score = max(score, 50)
        elif "content" in search_in and query_lower in db_prompt.content.lower():
            score = max(score, 10)
            
        return score

    def _db_prompt_to_model(self, db_prompt: DBPrompt) -> Prompt:
        """将数据库模型转换为Pydantic模型"""
        return Prompt(
            title=db_prompt.title,
            content=db_prompt.content,
            tags=[tag.name for tag in db_prompt.tags],
            remark=db_prompt.description or "",
            status=db_prompt.status,
            creator_username=db_prompt.creator_username,
            usage_count=db_prompt.usage_count,
            created_at=db_prompt.created_at,
            updated_at=db_prompt.updated_at,
            file_path=""  # 数据库模式下不需要文件路径
        )

    # ==================== 统计相关操作 ====================

    async def get_prompt_count_by_username(self, username: str) -> int:
        """获取指定用户创建的提示词数量"""
        async with AsyncSession(bind=async_engine) as session:
            result = await session.execute(
                select(func.count(DBPrompt.id)).where(DBPrompt.creator_username == username)
            )
            return result.scalar() or 0