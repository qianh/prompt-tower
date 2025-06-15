# 数据库迁移计划：提示管理系统

## 1. 引言

本文档概述了将提示管理系统的数据存储从当前基于文件的系统（JSON 和 YAML 文件）迁移到关系数据库的计划。此次迁移旨在提高数据完整性、可伸缩性、查询能力和整体系统鲁棒性。

## 2. 当前数据存储

目前，数据存储方式如下：

*   **用户 (Users)**: `backend/data/users.json` - 存储用户信息，包括用户名和哈希密码。
*   **标签 (Tags)**: `backend/data/tags.json` - 存储全局唯一标签列表。
*   **提示 (Prompts)**: `prompt-template/*.yaml` - 每个 YAML 文件代表一个提示，包含其内容、元数据、关联标签、状态等。

## 3. 已识别的API端点与数据操作

以下 API 端点涉及数据持久化，并将受到迁移的影响：

**认证 (`backend/api/auth.py`):**
*   `POST /auth/signup`: 创建新用户。(写入 `users.json`)
*   `POST /auth/login`: 认证用户。(读取 `users.json`)
*   `GET /auth/users/me`: 检索当前用户详情。(读取 `users.json`)

**大语言模型 (`backend/api/llm.py`):**
*   （此模块中未发现需要迁移的直接持久化数据存储操作。配置从设置中读取。）

**提示 (`backend/api/prompts.py`):**
*   `GET /prompts/`: 列出所有提示。(读取 `prompt-template/*.yaml`)
    *   支持按 `status` 和 `tag` 过滤。
*   `GET /prompts/tags/`: 获取提示中的所有唯一标签。(读取 `prompt-template/*.yaml`)
*   `GET /prompts/{title}`: 检索单个提示。(读取 `prompt-template/{title}.yaml`)
*   `POST /prompts/`: 创建新提示。(向 `prompt-template/` 写入新的 YAML 文件)
*   `PUT /prompts/{title}`: 更新现有提示。(修改 `prompt-template/{title}.yaml`)
*   `DELETE /prompts/{title}`: 删除提示。(删除 `prompt-template/{title}.yaml`)
*   `POST /prompts/search`: 搜索提示。(读取 `prompt-template/*.yaml` 的内容)
*   `POST /prompts/{title}/toggle-status`: 切换提示状态。(修改 `prompt-template/{title}.yaml`)
*   `POST /prompts/{title}/increment-usage`: 增加提示使用次数。(修改 `prompt-template/{title}.yaml`)

**标签 (`backend/api/tags.py`):**
*   `GET /tags`: 检索所有全局标签。(读取 `backend/data/tags.json`)
*   `POST /tags`: 添加新的全局标签。(写入 `backend/data/tags.json`)

**用户 (`backend/api/users.py`):**
*   `GET /users/`: 列出所有用户及其提示数量。(读取 `users.json` 并根据 `prompt-template/*.yaml` 计算每个用户的提示数量)
*   `GET /users/{username}/`: 获取特定用户详情及其提示数量。(读取 `users.json` 并根据 `prompt-template/*.yaml` 计算该用户的提示数量)

## 4. 建议的数据库解决方案

*   **关系数据库**: 推荐使用 PostgreSQL，因为它功能强大、特性丰富且对 Python 支持良好。MySQL 或 SQLite（适用于更简单的设置）也是可行的替代方案。
*   **ORM**: 推荐使用 SQLAlchemy 与数据库交互，它提供了强大而灵活的对象关系映射功能。
*   **迁移工具**: Alembic（与 SQLAlchemy 集成良好）用于管理数据库模式迁移。

## 5. 数据库模式设计

### 表: `users` (用户表)
*   `id`: INTEGER, PRIMARY KEY, AUTO_INCREMENT (整型，主键，自增)
*   `username`: VARCHAR(255), UNIQUE, NOT NULL (字符串，唯一，非空)
*   `hashed_password`: VARCHAR(255), NOT NULL (字符串，非空)
*   `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP (时间戳，默认为当前时间)
*   `updated_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP (时间戳，默认为当前时间)

### 表: `tags` (标签表)
*   `id`: INTEGER, PRIMARY KEY, AUTO_INCREMENT (整型，主键，自增)
*   `name`: VARCHAR(255), UNIQUE, NOT NULL (字符串，唯一，非空)
*   `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP (时间戳，默认为当前时间)

### 表: `prompts` (提示表)
*   `id`: INTEGER, PRIMARY KEY, AUTO_INCREMENT (整型，主键，自增)
*   `title`: VARCHAR(255), UNIQUE, NOT NULL (字符串，唯一，非空)
*   `content`: TEXT, NOT NULL (文本，非空)
*   `description`: TEXT (文本)
*   `creator_username`: VARCHAR(255), FOREIGN KEY REFERENCES `users(username)` (字符串，外键关联 `users` 表的 `username`)
*   `status`: VARCHAR(50), DEFAULT 'active' (字符串，默认为 'active'，例如：'active', 'inactive', 'archived')
*   `version`: VARCHAR(50) (字符串)
*   `usage_count`: INTEGER, DEFAULT 0 (整型，默认为 0)
*   `priority`: INTEGER, DEFAULT 0 (整型，默认为 0)
*   `settings`: JSONB (或 TEXT，如果 JSON 类型不可用) (JSONB 或文本)
*   `created_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP (时间戳，默认为当前时间)
*   `updated_at`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP (时间戳，默认为当前时间)

### 表: `prompt_tags` (提示-标签关联表，多对多关系)
*   `id`: INTEGER, PRIMARY KEY, AUTO_INCREMENT (整型，主键，自增)
*   `prompt_id`: INTEGER, FOREIGN KEY REFERENCES `prompts(id)` ON DELETE CASCADE (整型，外键关联 `prompts` 表的 `id`，级联删除)
*   `tag_id`: INTEGER, FOREIGN KEY REFERENCES `tags(id)` ON DELETE CASCADE (整型，外键关联 `tags` 表的 `id`，级联删除)
*   UNIQUE (`prompt_id`, `tag_id`) ( `prompt_id` 和 `tag_id` 组合唯一)

## 6. 迁移步骤

### 阶段 1: 准备与设置
1.  **备份数据**: 创建 `backend/data/users.json`, `backend/data/tags.json` 以及整个 `prompt-template/` 目录的备份。
2.  **安装数据库**: 安装 PostgreSQL (或选定的数据库)。
3.  **创建数据库**: 创建新的数据库实例 (例如, `prompt_system_db`)。
4.  **更新依赖**:
    *   将 `sqlalchemy`, `psycopg2-binary` (PostgreSQL 驱动), 和 `alembic` 添加到 `pyproject.toml`。
    *   运行 `uv pip install -e .` 安装新的依赖。
5.  **配置连接**:
    *   将数据库连接 URL (例如, `DATABASE_URL="postgresql://user:password@host:port/dbname"`) 添加到 `.env` 文件。
    *   更新 `backend/config.py` 以加载和解析此 `DATABASE_URL`。

### 阶段 2: 实现数据库模型与迁移
1.  **定义 SQLAlchemy 模型**:
    *   创建 `backend/db_models.py` (或类似文件)。
    *   定义与 `users`, `tags`, `prompts`, 和 `prompt_tags` 表相对应的 SQLAlchemy 类。
2.  **初始化 Alembic**:
    *   在项目根目录 (或 `backend/`) 运行 `alembic init alembic` 创建迁移环境。
    *   配置 `alembic/env.py` 以使用 `backend/config.py` 中的设置连接数据库，并识别 SQLAlchemy 模型。
3.  **创建初始迁移脚本**:
    *   运行 `alembic revision -m "create_initial_tables"` 生成新的迁移脚本。
    *   在生成的脚本中，使用 Alembic 的 `op` 函数 (例如, `op.create_table()`) 根据 SQLAlchemy 模型定义所有表的模式。
4.  **运行迁移**:
    *   执行 `alembic upgrade head` 应用迁移并在数据库中创建表。

### 阶段 3: 重构后端服务
1.  **数据库会话管理**:
    *   实现创建和管理数据库会话的机制 (例如, 使用 SQLAlchemy 的 `SessionLocal` 和 FastAPI 依赖)。
2.  **`user_service.py`**:
    *   将 JSON 文件操作替换为 SQLAlchemy 查询：
        *   `create_user_in_db`: 插入数据到 `users` 表。
        *   `get_user_by_username`: 从 `users` 表查询。
        *   `get_all_users`: 从 `users` 表查询所有数据。
3.  **`tag_service.py`**:
    *   将 JSON 文件操作替换为 SQLAlchemy 查询：
        *   `get_all_tags`: 从 `tags` 表查询所有数据。
        *   `add_tag`: 向 `tags` 表插入数据，处理唯一性。
4.  **`prompt_service.py`** (以及 `file_service.py` 中可能整合的逻辑):
    *   将 YAML 文件操作替换为 SQLAlchemy 查询：
        *   `list_prompts`: 从 `prompts` 表查询，包括与 `prompt_tags` 和 `tags` 表连接以实现按标签过滤。
        *   `get_all_tags` (来自提示): 通过 `prompt_tags` 查询与提示关联的唯一标签。
        *   `read_prompt` (按标题): 从 `prompts` 表查询。
        *   `create_prompt`: 向 `prompts` 表插入数据。管理 `prompt_tags` 关联。
        *   `update_prompt`: 更新 `prompts` 表。管理 `prompt_tags` 关联 (添加/删除标签)。
        *   `delete_prompt`: 从 `prompts` 表删除 (确保 `ON DELETE CASCADE` 处理 `prompt_tags`)。
        *   `search_prompts`: 使用 SQL `LIKE` 或全文搜索功能 (如果可用/已配置) 实现搜索逻辑。
        *   `toggle_prompt_status`: 更新 `prompts` 表中的 `status` 字段。
        *   `increment_usage_count`: 更新 `prompts` 表中的 `usage_count` 字段。
        *   `get_prompt_by_username_count`: 计算与用户关联的提示数量。
5.  **Pydantic 模型 (`backend/models.py`)**:
    *   确保现有的 Pydantic 模型与 SQLAlchemy 返回的数据兼容 (例如, 使用 `orm_mode = True` 或调整服务层的数据转换逻辑)。
    *   如果数据库结构差异较大，可能需要为请求/响应体创建新的 Pydantic 模型。

### 阶段 4: 数据迁移脚本
1.  **创建脚本**: 开发 Python 脚本 (例如, 在新的 `scripts/migration/` 目录下)，用于：
    *   连接到新的数据库。
    *   **迁移用户数据**:
        *   读取 `backend/data/users.json`。
        *   为每个用户在 `users` 表中���入一条记录。密码已经是哈希过的。
    *   **迁移标签数据**:
        *   读取 `backend/data/tags.json`。
        *   为每个标签在 `tags` 表中插入一条记录。
    *   **迁移提示及提示-标签关联数据**:
        *   遍历 `prompt-template/` 目录下的所有 `*.yaml` 文件。
        *   对于每个 YAML 文件：
            *   解析提示数据。
            *   在 `users` 表中查找或创建创建者用户。
            *   在 `prompts` 表中插入一条记录。
            *   对于与提示关联的每个标签：
                *   在 `tags` 表中查找或创建该标签。
                *   在 `prompt_tags` 表中插入一条记录，关联提示和标签。
2.  **运行脚本**: 仔细执行这些脚本，用现有数据填充新的数据库。

### 阶段 5: 测试
1.  **更新单元测试**:
    *   修改 `tests/` 目录中现有的 `pytest` 测试，以模拟数据库交互 (例如, 使用 `unittest.mock`) 或使用专用的测试数据库 (SQLite 内存数据库是个不错的选择)。
    *   重构服务层函数的测试，以断言正确的数据库调用和数据处理。
2.  **新测试**:
    *   为数据库特定的逻辑、约束和关系编写新的测试。
3.  **集成测试**:
    *   手动 (例如, 使用 Postman 或前端) 全面测试所有 API 端点，确保它们与新的数据库后端正常工作。
    *   测试用户注册、登录、提示创建/编辑/删除、标签管理和搜索功能。

### 阶段 6: 文档与清理
1.  **更新文档**:
    *   修改 `README.md` 和 `CLAUDE.md`，以反映新的数据库设置要求 (例如, PostgreSQL 安装, `.env` 文件中的 `DATABASE_URL` 变量)。
    *   记录 API 行为或数据结构的任何适用更改。
2.  **移除旧代码/数据**:
    *   一旦迁移得到验证并稳定运行，从服务中移除旧的文件 I/O 代码。
    *   在确保备份安全后，归档或删除 `backend/data/users.json`, `backend/data/tags.json` 文件以及 `prompt-template/` YAML 文件。

## 7. 回滚策略

如果在迁移过程中或迁移后立即出现严重问题：

1.  **恢复代码**: 检出应用迁移更改之前的先前提交。
2.  **恢复数据**:
    *   如果文件操作尚未移除，系统可能仍指向旧的数据文件。
    *   如有必要，从备份中恢复 `users.json`, `tags.json`, 和 `prompt-template/`。
3.  **数据库**: 新的数据库可以被删除或保留以供后续分析。
4.  **调查**: 在再次尝试迁移之前，分析失败原因。

## 8. 注意事项

*   **事务**: 在服务层函数中适当使用数据库事务以确保原子性，特别是对于涉及多个表写入的操作 (例如, 创建提示及其标签)。
*   **数据验证**: 继续在 API 层使用 Pydantic进行输入验证。SQLAlchemy 模型也可以进行一些验证。
*   **性能**:
    *   为 `WHERE` 子句、连接和 `ORDER BY` 中使用的关键列创建索引 (例如, `users.username`, `prompts.title`, `tags.name`, 外键)。
    *   监控查询性能并根据需要进行优化。
*   **安全**: 确保 `DATABASE_URL` (尤其是凭据) 在 `.env` 文件中保持安全，并且不提交到版本控制。
*   **密码哈希**: 当前的密码哈希机制 (`security.py`) 应保持不变；迁移后的哈希密码将按原样使用。
*   **并发**: 数据库将比文件系统更稳健地处理并发访问，但如果存在任何复杂的非原子操作，服务逻辑应注意潜在的竞争条件。
*   **现有用户 ID**: 如果 `users.json` 包含用户 ID，则需要决定是保留它们还是让新的 `users` 表自动生成 ID。为保持一致性，如果 `id` 是 `auth.py` 使用的 `User` 模型的一部分，则最好保留或映射它们。`CLAUDE.md` 中提供的当前 `users.json` 暗示存在 `id` 字段。如果它是 UUID 或字符串，模式应反映这一点；如果它是可能与自增冲突的整数，则可能需要在迁移期间采用映射策略或调整用户模型。（提供的 API 代码暗示使���了 `user.id`，因此需要仔细处理）。
*   **YAML 数据结构**: 确保 YAML 提示文件中的所有字段都映射到 `prompts` 表中的相应列，或者如果它们的结构化程度较低或差异很大，则存储在 JSONB `settings` 列中。

此计划提供了一个全面的路线图。每个步骤，尤其是在阶段3和阶段4中，都需要仔细的实施和测试。
