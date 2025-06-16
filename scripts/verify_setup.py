#!/usr/bin/env python3
"""
验证项目设置脚本 - 检查所有依赖和配置是否正确
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """测试关键模块导入"""
    print("🔍 Testing imports...")
    
    try:
        # 测试基础依赖
        import fastapi
        import uvicorn
        import pydantic
        import yaml
        import httpx
        print("✅ Basic dependencies imported successfully")
        
        # 测试数据库依赖
        import sqlalchemy
        import asyncpg
        import psycopg2
        print("✅ Database dependencies imported successfully")
        
        # 测试认证依赖
        import passlib
        import jose
        print("✅ Authentication dependencies imported successfully")
        
        # 测试LLM依赖
        import google.generativeai
        import openai
        print("✅ LLM dependencies imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_project_structure():
    """测试项目结构"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "backend/config.py",
        "backend/database.py", 
        "backend/db_models.py",
        "backend/services/db_service.py",
        "backend/services/unified_user_service.py",
        "backend/services/unified_tag_service.py",
        "scripts/migrate_to_database.py",
        "scripts/init_database.py",
        "scripts/test_migration.py",
        "MIGRATION_GUIDE.md",
        "pyproject.toml",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files present")
        return True


def test_config():
    """测试配置"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from backend.config import settings
        print(f"✅ Config loaded successfully")
        print(f"   USE_DATABASE: {settings.USE_DATABASE}")
        print(f"   DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        print(f"   API_HOST: {settings.API_HOST}")
        print(f"   API_PORT: {settings.API_PORT}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False


def test_database_models():
    """测试数据库模型"""
    print("\n🗄️  Testing database models...")
    
    try:
        from backend.db_models import User, Tag, Prompt, PromptTag
        print("✅ Database models imported successfully")
        print(f"   User table: {User.__tablename__}")
        print(f"   Tag table: {Tag.__tablename__}")
        print(f"   Prompt table: {Prompt.__tablename__}")
        print(f"   PromptTag table: {PromptTag.__tablename__}")
        return True
    except Exception as e:
        print(f"❌ Database models error: {e}")
        return False


def test_services():
    """测试服务层"""
    print("\n🔧 Testing services...")
    
    try:
        from backend.services.unified_user_service import user_service
        from backend.services.unified_tag_service import tag_service
        from backend.services.db_service import DatabaseService
        print("✅ Services imported successfully")
        return True
    except Exception as e:
        print(f"❌ Services error: {e}")
        return False


def main():
    """主函数"""
    print("🚀 Verifying Prompt Management System setup...")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Configuration", test_config),
        ("Database Models", test_database_models),
        ("Services", test_services),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 Verification Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Setup verification successful!")
        print("\nNext steps:")
        print("1. Configure your database (if using database mode)")
        print("2. Update .env file with your API keys")
        print("3. Run: uv run python scripts/init_database.py (for database mode)")
        print("4. Run: ./scripts/start.sh")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)