# 数据库迁移指南

本指南将帮助您将Prompt管理系统从文件存储迁移到PostgreSQL数据库。

## 🎯 迁移概述

迁移包括以下步骤：
1. 安装数据库依赖
2. 配置PostgreSQL数据库
3. 初始化数据库表结构
4. 迁移现有数据
5. 切换到数据库模式
6. 验证迁移结果

## 📋 前置条件

### 1. 安装PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (使用Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
下载并安装 [PostgreSQL官方安装包](https://www.postgresql.org/download/windows/)

### 2. 创建数据库和用户

```sql
-- 连接到PostgreSQL
sudo -u postgres psql

-- 创建数据库用户
CREATE USER prompt_user WITH PASSWORD 'your_secure_password';

-- 创建数据库
CREATE DATABASE prompt_management OWNER prompt_user;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE prompt_management TO prompt_user;

-- 退出
\q
```

## 🔧 迁移步骤

### 步骤1: 安装依赖

```bash
# 使用uv安装项目依赖（已包含数据库支持）
uv pip install -e .

# 或者如果需要开发依赖
uv pip install -e ".[dev]"
```

### 步骤2: 配置数据库连接

编辑 `.env` 文件，更新数据库配置：

```env
# 数据库配置
USE_DATABASE=False  # 先保持False，迁移完成后改为True
DATABASE_URL=postgresql://prompt_user:your_secure_password@localhost/prompt_management
ASYNC_DATABASE_URL=postgresql+asyncpg://prompt_user:your_secure_password@localhost/prompt_management
```

### 步骤3: 初始化数据库表

```bash
# 运行数据库初始化脚本
uv run python scripts/init_database.py
```

### 步骤4: 迁移现有数据

```bash
# 运行数据迁移脚本
uv run python scripts/migrate_to_database.py
```

迁移脚本将会：
- 迁移 `backend/data/users.json` 中的用户数据
- 迁移 `backend/data/tags.json` 中的标签数据  
- 迁移 `prompt-template/*.yaml` 中的提示词数据
- 建立提示词和标签的关联关系

### 步骤5: 切换到数据库模式

迁移完成后，更新 `.env` 文件：

```env
USE_DATABASE=True  # 启用数据库模式
```

### 步骤6: 重启应用

```bash
# 重启应用以使用数据库模式
./scripts/start.sh
```

## 🔍 验证迁移

### 1. 检查数据库内容

```sql
-- 连接到数据库
psql -U prompt_user -d prompt_management

-- 检查表和数据
\dt  -- 列出所有表

SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM tags;
SELECT COUNT(*) FROM prompts;
SELECT COUNT(*) FROM prompt_tags;

-- 查看具体数据
SELECT username FROM users LIMIT 5;
SELECT name FROM tags LIMIT 10;
SELECT title, status FROM prompts LIMIT 5;
```

### 2. 测试API功能

```bash
# 测试健康检查
curl http://localhost:8010/health

# 测试用户登录
curl -X POST http://localhost:8010/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"

# 测试获取提示词列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8010/api/v1/prompts/
```

## 🔄 回滚方案

如果迁移出现问题，可以快速回滚到文件模式：

1. 更新 `.env` 文件：
   ```env
   USE_DATABASE=False
   ```

2. 重启应用：
   ```bash
   ./scripts/start.sh
   ```

原始的文件数据不会被删除，应用会继续使用文件存储。

## 📊 性能对比

| 功能 | 文件模式 | 数据库模式 |
|------|----------|------------|
| 查询速度 | 较慢 | 快速 |
| 并发支持 | 有限 | 优秀 |
| 数据一致性 | 基本 | 强一致性 |
| 搜索功能 | 基础 | 高级 |
| 扩展性 | 有限 | 优秀 |

## 🚨 注意事项

1. **备份数据**: 迁移前请备份 `backend/data/` 和 `prompt-template/` 目录
2. **数据库权限**: 确保数据库用户有足够的权限
3. **连接配置**: 检查数据库连接字符串是否正确
4. **防火墙**: 确保数据库端口（默认5432）可访问
5. **内存使用**: 数据库模式可能使用更多内存

## 🛠️ 故障排除

### 常见问题

**1. 连接数据库失败**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
- 检查PostgreSQL服务是否运行
- 验证数据库连接字符串
- 检查防火墙设置

**2. 权限错误**
```
psycopg2.errors.InsufficientPrivilege: permission denied
```
- 确保数据库用户有足够权限
- 重新授予权限：`GRANT ALL PRIVILEGES ON DATABASE prompt_management TO prompt_user;`

**3. 表已存在错误**
```
sqlalchemy.exc.ProgrammingError: relation "users" already exists
```
- 这是正常的，表创建脚本使用了 `IF NOT EXISTS`
- 可以安全忽略此警告

**4. 迁移数据重复**
```
IntegrityError: duplicate key value violates unique constraint
```
- 迁移脚本会检查重复数据
- 如果出现此错误，可能需要清理数据库后重新迁移

### 获取帮助

如果遇到问题，请：
1. 检查应用日志
2. 查看数据库日志
3. 确认配置文件设置
4. 参考项目文档

## 📈 后续优化

迁移完成后，可以考虑以下优化：

1. **索引优化**: 根据查询模式添加合适的索引
2. **连接池**: 配置数据库连接池参数
3. **监控**: 设置数据库性能监控
4. **备份**: 建立定期数据库备份策略
5. **缓存**: 考虑添加Redis缓存层

---

🎉 恭喜！您已成功完成数据库迁移。现在您的Prompt管理系统具备了更好的性能、可扩展性和数据一致性。