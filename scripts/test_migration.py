#!/usr/bin/env python3
"""
迁移测试脚本 - 验证数据库迁移是否成功
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.services.db_service import DatabaseService
from backend.services.unified_user_service import user_service
from backend.services.unified_tag_service import tag_service


async def test_database_connection():
    """测试数据库连接"""
    print("🔗 Testing database connection...")
    
    try:
        db_service = DatabaseService()
        users = await db_service.get_all_users()
        print(f"✅ Database connection successful. Found {len(users)} users.")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_user_service():
    """测试用户服务"""
    print("\n👤 Testing user service...")
    
    try:
        users = await user_service.get_all_users()
        print(f"✅ User service working. Found {len(users)} users.")
        
        if users:
            sample_user = users[0]
            print(f"   Sample user: {sample_user.username} (ID: {sample_user.id})")
        
        return True
    except Exception as e:
        print(f"❌ User service test failed: {e}")
        return False


async def test_tag_service():
    """测试标签服务"""
    print("\n🏷️  Testing tag service...")
    
    try:
        tags = await tag_service.get_all_tags()
        print(f"✅ Tag service working. Found {len(tags)} tags.")
        
        if tags:
            print(f"   Sample tags: {tags[:5]}")
        
        return True
    except Exception as e:
        print(f"❌ Tag service test failed: {e}")
        return False


async def test_prompt_service():
    """测试提示词服务"""
    print("\n📝 Testing prompt service...")
    
    try:
        if settings.USE_DATABASE:
            db_service = DatabaseService()
            prompts = await db_service.list_prompts()
        else:
            from backend.services.file_service import FileService
            file_service = FileService()
            prompts = await file_service.list_prompts()
        
        print(f"✅ Prompt service working. Found {len(prompts)} prompts.")
        
        if prompts:
            sample_prompt = prompts[0]
            print(f"   Sample prompt: '{sample_prompt.title}' (Status: {sample_prompt.status})")
            print(f"   Tags: {sample_prompt.tags}")
        
        return True
    except Exception as e:
        print(f"❌ Prompt service test failed: {e}")
        return False


async def test_data_consistency():
    """测试数据一致性"""
    print("\n🔍 Testing data consistency...")
    
    try:
        if not settings.USE_DATABASE:
            print("⚠️  Skipping consistency test (file mode)")
            return True
        
        db_service = DatabaseService()
        
        # 检查用户-提示词关联
        prompts = await db_service.list_prompts()
        users = await db_service.get_all_users()
        
        user_names = {user.username for user in users}
        
        orphaned_prompts = []
        for prompt in prompts:
            if prompt.creator_username and prompt.creator_username not in user_names:
                orphaned_prompts.append(prompt.title)
        
        if orphaned_prompts:
            print(f"⚠️  Found {len(orphaned_prompts)} prompts with invalid creators:")
            for title in orphaned_prompts[:5]:
                print(f"     - {title}")
        else:
            print("✅ All prompts have valid creators or no creator assigned.")
        
        # 检查标签-提示词关联
        tags = await db_service.get_all_tags()
        print(f"✅ Data consistency check completed. {len(tags)} tags, {len(prompts)} prompts.")
        
        return True
    except Exception as e:
        print(f"❌ Data consistency test failed: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🧪 Running migration tests...")
    print("=" * 50)
    
    print(f"📊 Current mode: {'Database' if settings.USE_DATABASE else 'File'}")
    print(f"🔗 Database URL: {settings.DATABASE_URL}")
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Service", test_user_service),
        ("Tag Service", test_tag_service),
        ("Prompt Service", test_prompt_service),
        ("Data Consistency", test_data_consistency),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Migration appears successful.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False


async def main():
    """主函数"""
    try:
        success = await run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())