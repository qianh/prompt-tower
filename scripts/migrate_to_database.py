#!/usr/bin/env python3
"""
数据迁移脚本：从文件存储迁移到数据库
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import async_engine, Base
from backend.db_models import User as DBUser, Tag as DBTag, Prompt as DBPrompt
from backend.services.db_service import DatabaseService
from backend.utils.security import get_password_hash


class DataMigrator:
    """数据迁移器"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.data_dir = Path(__file__).parent.parent / "backend" / "data"
        self.prompt_dir = Path(__file__).parent.parent / "prompt-template"
        
    async def create_tables(self):
        """创建数据库表"""
        print("Creating database tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
    
    async def migrate_users(self) -> Dict[str, int]:
        """迁移用户数据"""
        print("\n📁 Migrating users...")
        users_file = self.data_dir / "users.json"
        
        if not users_file.exists():
            print("⚠️  No users.json file found, skipping user migration")
            return {}
        
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users_data = data.get("users", [])
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Error reading users.json: {e}")
            return {}
        
        username_to_id = {}
        migrated_count = 0
        
        async with AsyncSession(bind=async_engine) as session:
            for user_data in users_data:
                try:
                    # 检查用户是否已存在
                    existing_user = await session.get(DBUser, user_data.get("id"))
                    if existing_user:
                        print(f"   User {user_data['username']} already exists, skipping")
                        username_to_id[user_data['username']] = existing_user.id
                        continue
                    
                    # 创建新用户
                    db_user = DBUser(
                        id=user_data.get("id"),
                        username=user_data["username"],
                        hashed_password=user_data["hashed_password"]
                    )
                    session.add(db_user)
                    await session.flush()
                    
                    username_to_id[user_data['username']] = db_user.id
                    migrated_count += 1
                    print(f"   ✅ Migrated user: {user_data['username']}")
                    
                except Exception as e:
                    print(f"   ❌ Error migrating user {user_data.get('username', 'unknown')}: {e}")
                    continue
            
            await session.commit()
        
        print(f"✅ Users migration completed: {migrated_count} users migrated")
        return username_to_id
    
    async def migrate_tags(self) -> Dict[str, int]:
        """迁移标签数据"""
        print("\n🏷️  Migrating tags...")
        tags_file = self.data_dir / "tags.json"
        
        if not tags_file.exists():
            print("⚠️  No tags.json file found, skipping tag migration")
            return {}
        
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Error reading tags.json: {e}")
            return {}
        
        tag_name_to_id = {}
        migrated_count = 0
        
        async with AsyncSession(bind=async_engine) as session:
            for tag_name in tags_data:
                try:
                    if not tag_name.strip():
                        continue
                    
                    # 检查标签是否已存在
                    from sqlalchemy import select, func
                    result = await session.execute(
                        select(DBTag).where(func.lower(DBTag.name) == tag_name.lower())
                    )
                    existing_tag = result.scalar_one_or_none()
                    
                    if existing_tag:
                        print(f"   Tag '{tag_name}' already exists, skipping")
                        tag_name_to_id[tag_name] = existing_tag.id
                        continue
                    
                    # 创建新标签
                    db_tag = DBTag(name=tag_name.strip())
                    session.add(db_tag)
                    await session.flush()
                    
                    tag_name_to_id[tag_name] = db_tag.id
                    migrated_count += 1
                    print(f"   ✅ Migrated tag: {tag_name}")
                    
                except Exception as e:
                    print(f"   ❌ Error migrating tag '{tag_name}': {e}")
                    continue
            
            await session.commit()
        
        print(f"✅ Tags migration completed: {migrated_count} tags migrated")
        return tag_name_to_id
    
    async def migrate_prompts(self, tag_name_to_id: Dict[str, int]):
        """迁移提示词数据"""
        print("\n📝 Migrating prompts...")
        
        if not self.prompt_dir.exists():
            print("⚠️  No prompt-template directory found, skipping prompt migration")
            return
        
        yaml_files = list(self.prompt_dir.glob("*.yaml"))
        if not yaml_files:
            print("⚠️  No YAML files found in prompt-template directory")
            return
        
        migrated_count = 0
        error_count = 0
        
        async with AsyncSession(bind=async_engine) as session:
            for yaml_file in yaml_files:
                try:
                    # 读取YAML文件
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        prompt_data = yaml.safe_load(f)
                    
                    if not isinstance(prompt_data, dict):
                        print(f"   ❌ Invalid YAML format in {yaml_file.name}")
                        error_count += 1
                        continue
                    
                    title = prompt_data.get("title", yaml_file.stem)
                    
                    # 检查提示词是否已存在
                    from sqlalchemy import select
                    result = await session.execute(
                        select(DBPrompt).where(DBPrompt.title == title)
                    )
                    existing_prompt = result.scalar_one_or_none()
                    
                    if existing_prompt:
                        print(f"   Prompt '{title}' already exists, skipping")
                        continue
                    
                    # 获取文件时间戳
                    stat = yaml_file.stat()
                    from datetime import datetime
                    created_at = datetime.fromtimestamp(stat.st_ctime)
                    updated_at = datetime.fromtimestamp(stat.st_mtime)
                    
                    # 创建新提示词
                    db_prompt = DBPrompt(
                        title=title,
                        content=prompt_data.get("content", ""),
                        description=prompt_data.get("remark", ""),
                        creator_username=prompt_data.get("creator_username"),
                        status=prompt_data.get("status", "enabled"),
                        usage_count=prompt_data.get("usage_count", 0),
                        created_at=created_at,
                        updated_at=updated_at,
                        settings={}
                    )
                    session.add(db_prompt)
                    await session.flush()
                    
                    # 处理标签关联
                    tags = prompt_data.get("tags", [])
                    if tags:
                        for tag_name in tags:
                            if not tag_name or not tag_name.strip():
                                continue
                            
                            tag_name = tag_name.strip()
                            
                            # 获取或创建标签
                            tag_id = tag_name_to_id.get(tag_name)
                            if not tag_id:
                                # 创建新标签
                                db_tag = DBTag(name=tag_name)
                                session.add(db_tag)
                                await session.flush()
                                tag_id = db_tag.id
                                tag_name_to_id[tag_name] = tag_id
                            
                            # 创建标签关联
                            from backend.db_models import PromptTag
                            prompt_tag = PromptTag(prompt_id=db_prompt.id, tag_id=tag_id)
                            session.add(prompt_tag)
                    
                    migrated_count += 1
                    print(f"   ✅ Migrated prompt: {title}")
                    
                except Exception as e:
                    print(f"   ❌ Error migrating prompt from {yaml_file.name}: {e}")
                    error_count += 1
                    continue
            
            await session.commit()
        
        print(f"✅ Prompts migration completed: {migrated_count} prompts migrated, {error_count} errors")
    
    async def verify_migration(self):
        """验证迁移结果"""
        print("\n🔍 Verifying migration...")
        
        async with AsyncSession(bind=async_engine) as session:
            # 统计用户数量
            from sqlalchemy import select, func
            user_count = await session.scalar(select(func.count(DBUser.id)))
            print(f"   Users in database: {user_count}")
            
            # 统计标签数量
            tag_count = await session.scalar(select(func.count(DBTag.id)))
            print(f"   Tags in database: {tag_count}")
            
            # 统计提示词数量
            prompt_count = await session.scalar(select(func.count(DBPrompt.id)))
            print(f"   Prompts in database: {prompt_count}")
            
            # 统计标签关联数量
            from backend.db_models import PromptTag
            prompt_tag_count = await session.scalar(select(func.count(PromptTag.id)))
            print(f"   Prompt-tag associations: {prompt_tag_count}")
        
        print("✅ Migration verification completed")
    
    async def run_migration(self):
        """运行完整的迁移流程"""
        print("🚀 Starting data migration from files to database...")
        print("=" * 60)
        
        try:
            # 1. 创建数据库表
            await self.create_tables()
            
            # 2. 迁移用户
            username_to_id = await self.migrate_users()
            
            # 3. 迁移标签
            tag_name_to_id = await self.migrate_tags()
            
            # 4. 迁移提示词
            await self.migrate_prompts(tag_name_to_id)
            
            # 5. 验证迁移结果
            await self.verify_migration()
            
            print("\n" + "=" * 60)
            print("🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Update your .env file to set USE_DATABASE=True")
            print("2. Update DATABASE_URL and ASYNC_DATABASE_URL with your database credentials")
            print("3. Restart your application")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


async def main():
    """主函数"""
    migrator = DataMigrator()
    await migrator.run_migration()


if __name__ == "__main__":
    asyncio.run(main())