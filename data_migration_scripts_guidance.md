# 数据库操作脚本指南 (DDL, DML 迁移, DQL 示例)

本文档提供生成数据库DDL（数据定义语言）的脚本，并指导如何创建DML（数据操作语言）脚本以进行数据迁移，同时提供一些DQL（数据查询语言）的示例。

## 1. DDL (数据定义语言) 脚本

用于创建数据库表结构（表、索引、外键等）的SQL DDL脚本已在 `database_schema.sql` 文件中提供。您可以直接在您的PostgreSQL数据库（或相应调整后用于其他SQL数据库）中执行此脚本以创建必要的表。

**执行DDL脚本 (PostgreSQL示例):**
```bash
psql -U your_username -d your_database_name -a -f database_schema.sql
```
(请根据您的数据库类型、用户名、数据库名和连接方式调整上述命令。`-a`会回显所有行，`-f`指定文件。)

## 2. DML (数据操作语言) - 数据迁移脚本指南

将现有数据（来自 `backend/data/users.json`, `backend/data/tags.json`, 和 `prompt-template/*.yaml`）迁移到新创建的数据库表中，需要自定义脚本。正如 `DATABASE_MIGRATION_PLAN.md` (中文版) 中第6阶段第4部分所述，推荐使用Python脚本来完成此任务，并配合SQLAlchemy等ORM或数据库驱动（如psycopg2）。

以下是为每个表编写迁移脚本时，可以使用的SQL INSERT语句模板和大致步骤：

### a. 迁移用户 (`users` 表)

*   **源文件**: `backend/data/users.json`
*   **读取逻辑**:
    1.  解析JSON文件 (通常是一个用户对象列表)。
    2.  对于每个用户对象，提取 `id` (若要保留旧ID且新ID列允许手动插入，或有映射表；若`id`为`SERIAL`且希望数据库生成，则不插入`id`), `username`, `hashed_password`。
    3.  `created_at` 和 `updated_at` 字段: 若JSON中有且希望保留，则在INSERT时提供；否则数据库将使用默认值 (CURRENT_TIMESTAMP)。

*   **SQL INSERT 模板 (使用 psycopg2 Python 示例)**:
    ```python
    import json
    import psycopg2 # or your DB driver
    # conn = psycopg2.connect(...) # Establish connection
    # cur = conn.cursor()

    with open('backend/data/users.json', 'r') as f:
        users_data = json.load(f) # Assuming it's a list of user dicts

    for user in users_data:
        # Assuming users.json does not contain 'id' to be inserted, as 'id' is SERIAL
        # If users.json has an 'id' you want to use, ensure the 'id' column in DB is not SERIAL or allows explicit insert.
        try:
            sql = """
            INSERT INTO users (username, hashed_password) 
            VALUES (%s, %s) RETURNING id;
            """
            # Add created_at, updated_at if they are in user dict and you want to set them manually
            # sql = "INSERT INTO users (username, hashed_password, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING id;"
            # cur.execute(sql, (user['username'], user['hashed_password'], user.get('created_at'), user.get('updated_at')))
            
            cur.execute(sql, (user['username'], user['hashed_password']))
            user_id = cur.fetchone()[0]
            print(f"Inserted user {user['username']} with new id {user_id}")
            # conn.commit() # Commit per user or in batch
        except Exception as e:
            print(f"Error inserting user {user.get('username')}: {e}")
            # conn.rollback()
    # conn.close()
    ```

### b. 迁移全局标签 (`tags` 表)

*   **源文件**: `backend/data/tags.json` (通常是一个标签名称字符串列表)
*   **读取逻辑**:
    1.  解析JSON文件。
    2.  对于列表中的每个标签名称，插入到 `tags` 表。`name` 字段是唯一的。

*   **SQL INSERT 模板 (psycopg2 Python)**:
    ```python
    # ... (connection setup) ...
    with open('backend/data/tags.json', 'r') as f:
        tags_list = json.load(f)

    for tag_name in tags_list:
        try:
            sql = """
            INSERT INTO tags (name) VALUES (%s) 
            ON CONFLICT (name) DO NOTHING RETURNING id; 
            """
            # ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id; # If you want to update existing
            cur.execute(sql, (tag_name,))
            tag_id_result = cur.fetchone()
            if tag_id_result:
                print(f"Inserted/Found tag '{tag_name}' with id {tag_id_result[0]}")
            else:
                # If DO NOTHING and it conflicted, fetch the existing one
                cur.execute("SELECT id FROM tags WHERE name = %s;", (tag_name,))
                tag_id_result = cur.fetchone()
                if tag_id_result:
                    print(f"Tag '{tag_name}' already exists with id {tag_id_result[0]}")

            # conn.commit()
        except Exception as e:
            print(f"Error inserting tag {tag_name}: {e}")
            # conn.rollback()
    # ... (connection close) ...
    ```

### c. 迁移提示 (`prompts` 表) 和 提示-标签关联 (`prompt_tags` 表)

*   **源文件**: `prompt-template/*.yaml`
*   **读取逻辑**:
    1.  遍历所有YAML文件。
    2.  为每个文件解析内容：`title`, `content`, `description`, `creator_username`, `status`, `version`, `usage_count`, `priority`, `settings` (字典), `tags` (列表)。
    3.  **插入Prompts**:
        *   `creator_username` 用于外键关联。
        *   将解析的数据插入 `prompts` 表。获取新生成的 `prompt_id`。
    4.  **处理标签和关联**:
        *   对于该prompt的每个标签 (来自YAML中的 `tags` 列表):
            *   在 `tags` 表中查找或创建该标签 (使用与上述类似的 `INSERT ... ON CONFLICT ... RETURNING id` 逻辑)。获取 `tag_id`。
            *   在 `prompt_tags` 表中插入 `prompt_id` 和 `tag_id` 的关联。

*   **SQL INSERT 模板 (Prompts - psycopg2 Python)**:
    ```python
    import yaml
    import os
    import json # For settings JSONB field
    # ... (connection setup) ...

    prompt_template_dir = 'prompt-template/'
    for filename in os.listdir(prompt_template_dir):
        if filename.endswith('.yaml'):
            filepath = os.path.join(prompt_template_dir, filename)
            with open(filepath, 'r') as f:
                prompt_data = yaml.safe_load(f)
            
            try:
                # Convert settings dict to JSON string for JSONB field
                settings_json = json.dumps(prompt_data.get('settings', {}))

                sql_prompt = """
                INSERT INTO prompts (title, content, description, creator_username, status, 
                                     version, usage_count, priority, settings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
                """
                cur.execute(sql_prompt, (
                    prompt_data['title'], prompt_data['content'], prompt_data.get('description'),
                    prompt_data.get('creator_username'), prompt_data.get('status', 'active'),
                    prompt_data.get('version'), prompt_data.get('usage_count', 0),
                    prompt_data.get('priority', 0), settings_json
                ))
                current_prompt_id = cur.fetchone()[0]
                print(f"Inserted prompt '{prompt_data['title']}' with id {current_prompt_id}")

                # Handle prompt_tags associations
                if 'tags' in prompt_data and isinstance(prompt_data['tags'], list):
                    for tag_name in prompt_data['tags']:
                        # Get or create tag_id (similar to section b)
                        cur.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id;", (tag_name,))
                        # If using DO NOTHING:
                        # cur.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;", (tag_name,))
                        tag_id_result = cur.fetchone()
                        current_tag_id = None
                        if tag_id_result:
                           current_tag_id = tag_id_result[0]
                        else: # Tag existed, DO NOTHING was hit
                           cur.execute("SELECT id FROM tags WHERE name = %s;", (tag_name,))
                           current_tag_id = cur.fetchone()[0]

                        if current_tag_id and current_prompt_id:
                            sql_associate_tag = """
                            INSERT INTO prompt_tags (prompt_id, tag_id) VALUES (%s, %s)
                            ON CONFLICT (prompt_id, tag_id) DO NOTHING;
                            """
                            cur.execute(sql_associate_tag, (current_prompt_id, current_tag_id))
                # conn.commit()
            except Exception as e:
                print(f"Error inserting prompt {prompt_data.get('title')}: {e}")
                # conn.rollback()
    # ... (connection close) ...
    ```

**重要**: 
*   上述Python中的SQL示例使用了psycopg2的参数化查询 (`%s`)，这是防止SQL注入的正确做法。
*   错误处理和事务管理 (commit/rollback) 应根据您的需求仔细实现。
*   确保 `creator_username` 在 `users` 表中存在，或者��据库外键约束允许 `NULL`。

## 3. DQL (数据查询语言) - 示例脚本

以下是一些基于新数据库模式的常见数据查询示例：

### a. 获取所有用户及其提示数量
```sql
SELECT
    u.id,
    u.username,
    u.created_at,
    COUNT(p.id) AS prompt_count
FROM
    users u
LEFT JOIN
    prompts p ON u.username = p.creator_username
GROUP BY
    u.id, u.username, u.created_at
ORDER BY
    u.username;
```

### b. 获取特定用户创建的所有提示
```sql
SELECT
    p.id,
    p.title,
    p.status,
    p.usage_count,
    p.created_at,
    p.updated_at
FROM
    prompts p
WHERE
    p.creator_username = 'specific_username'; -- 使用参数绑定
```

### c. 列出所有提示，并附带其标签 (逗号分隔)
```sql
SELECT
    p.id,
    p.title,
    p.status,
    STRING_AGG(t.name, ', ' ORDER BY t.name) AS tags
FROM
    prompts p
LEFT JOIN
    prompt_tags pt ON p.id = pt.prompt_id
LEFT JOIN
    tags t ON pt.tag_id = t.id
GROUP BY
    p.id, p.title, p.status
ORDER BY
    p.title;
```

### d. 根据标签过滤提示
```sql
SELECT
    p.id,
    p.title,
    p.status
FROM
    prompts p
JOIN
    prompt_tags pt ON p.id = pt.prompt_id
JOIN
    tags t ON pt.tag_id = t.id
WHERE
    t.name = 'desired_tag_name'; -- 使用参数绑定
```

### e. 获取所有全��标签
```sql
SELECT id, name, created_at FROM tags ORDER BY name;
```

这些脚本和指南应能帮助您完成数据库的设置和数据迁移。请参考 `DATABASE_MIGRATION_PLAN.md` (中文版) 获取更详细的迁移步骤和逻辑。
