#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import async_engine, Base


async def init_database():
    """初始化数据库表"""
    print("🚀 Initializing database...")
    
    try:
        async with async_engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        print("\nCreated tables:")
        print("- users")
        print("- tags") 
        print("- prompts")
        print("- prompt_tags")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())