# Prompt管理系统

一个基于Python和React的Prompt管理系统，支持MCP Server协议，提供完整的prompt管理功能和LLM优化能力。

## 功能特性

### 网页部分

- ✅ **基础管理功能**：查询、复制、编辑、启用/禁用prompt
- ✅ **智能搜索**：支持按标题、标签、内容关键词搜索
- ✅ **LLM优化**：集成Gemini、Qwen、DeepSeek等LLM，自动优化prompt
- ✅ **实时同步**：所有生效的prompt自动同步到MCP Server

### 数据存储

- ✅ **双模式支持**：支持文件存储和PostgreSQL数据库存储
- ✅ **无缝迁移**：提供完整的数据迁移工具和指南
- ✅ **高性能查询**：数据库模式支持复杂查询和索引优化
- ✅ **数据一致性**：关系型数据库确保数据完整性

### 用户认证
- ✅ **用户注册与登录**: 支持用户通过用户名和密码注册及登录。
- ✅ **JWT安全认证**: 后端API使用JSON Web Tokens (JWT)进行安全认证。
- ✅ **受保护的路由**: 前后端均实现路由保护，确保敏感操作和数据仅对已认证用户开放。
- ✅ **用户数据存储**: 支持文件系统存储 (`backend/data/users.json`) 和PostgreSQL数据库存储。

### MCP Server

- ✅ **标准协议**：支持Streamablehttp协议调用
- ✅ **高效检索**：按优先级（标题>标签>内容）检索prompt
- ✅ **批量输出**：支持多结果列表输出
- ✅ **实时更新**：自动加载最新的prompt模板

## 技术栈

- **后端**：Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, uv, passlib[bcrypt], python-jose[cryptography]
- **前端**：React 18, Ant Design 5, React Router DOM
- **数据库**：PostgreSQL (可选), 文件存储 (默认)
- **LLM支持**：Gemini, Qwen, DeepSeek
- **协议**：MCP (Model Context Protocol)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/prompt-management-system.git
cd prompt-management-system
```

### 2. 环境准备与依赖安装

**后端:**
- 确保已安装 Python 3.11+ 和 uv。
- 在项目根目录，安装后端依赖:
  ```bash
  # 安装项目依赖（包括数据库支持）
  uv pip install -e .
  
  # 或者安装开发依赖
  uv pip install -e ".[dev]"
  ```
- (可选但推荐) 创建并激活虚拟环境:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # macOS/Linux
  # .venv\Scripts\activate    # Windows
  # 然后执行 uv pip install ...
  ```
- 复制 `.env.example` 为 `.env` 并根据需要配置其中的环境变量 (如LLM API Keys, 以及用于JWT的 `SECRET_KEY`)。`SECRET_KEY` 至关重要，请确保其足够复杂和安全。

**前端:**
- 确保已安装 Node.js 和 npm (或 yarn).
- 进入 `frontend` 目录并安装依赖:
  ```bash
  cd frontend
  npm install
  cd ..
  ```

### 3. 运行应用

**启动后端服务:**
```bash
# 从项目根目录
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8010 --reload
```

**启动前端开发服务:**
```bash
# 从项目根目录
cd frontend
npm start
```

**启动MCP Server (如果需要):**
```bash
# 从项目根目录
python mcp_server/server.py
```

### 4. 数据库配置 (可选)

系统默认使用文件存储，如需使用PostgreSQL数据库：

**安装PostgreSQL并创建数据库:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createuser --interactive prompt_user
sudo -u postgres createdb prompt_management -O prompt_user
```

**配置数据库连接** (在 `.env` 文件中):
```env
USE_DATABASE=True
DATABASE_URL=postgresql://prompt_user:password@localhost/prompt_management
ASYNC_DATABASE_URL=postgresql+asyncpg://prompt_user:password@localhost/prompt_management
```

**初始化数据库表:**
```bash
uv run python scripts/init_database.py
```

**迁移现有数据** (如果有文件数据):
```bash
uv run python scripts/migrate_to_database.py
```

**测试迁移结果:**
```bash
uv run python scripts/test_migration.py
```

详细迁移指南请参考 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

## 整体架构图

```txt
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器                              │
│                   React Frontend (React Router)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  登录/注册 | 查询 | 复制 | 编辑 | 启用/禁用 | LLM优化 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬────────────────��──────────────────────┘
                      │ HTTP/REST API (部分受JWT保护)
┌─────────────────────┴───────────────────────────────────────┐
│                  Python Backend (FastAPI)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Auth API | Prompt管理API | LLM集成 | 存储管理        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                 │                 │
│  ┌───────────────────────┴─┐  ┌────────────┴───────────┐   │
│  │  文件存储 (默认)        │  │  PostgreSQL数据库 (可选) │   │
│  │  - prompt-template/     │  │  - users表              │   │
│  │  - backend/data/        │  │  - prompts表            │   │
│  │                         │  │  - tags表               │   │
│  └─────────────────────────┘  └────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 共享数据 (Prompts)
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    MCP Server (Python)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   Streamablehttp协议 | 检索功能 | 优先级排序       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    MCP Client (Cursor/Windsurf等)
```

## 项目目录结构

```txt
prompt-management-system/
├── pyproject.toml                 # uv项目配置文件
├── README.md                      # 项目说明文档
├── .env.example                   # 环境变量示例
├── .gitignore
│
├── backend/                       # Python后端
│   ├── __init__.py
│   ├── main.py                   # FastAPI主入口
│   ├── config.py                 # 配置管理
│   ├── models.py                 # 数据模型
│   ├── data/                     # 数据存储
│   │   └── .gitkeep              # (users.json在此目录运行时创建)
│   ├── api/                      # API路由
│   │   ├── __init__.py
│   │   ├── auth.py              # 用户认证API
│   │   ├── prompts.py           # Prompt管理API
│   │   └── llm.py               # LLM相关API
│   ├── services/                 # 业务逻辑
│   │   ├── __init__.py
│   │   ├── user_service.py      # 用户管理服务
│   │   ├── prompt_service.py    # Prompt管理服务
│   │   ├── llm_service.py       # LLM服务
│   │   └── file_service.py      # 文件管理服务
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── security.py          # 密码哈希辅助函数
│       ├── jwt_helpers.py       # JWT 创建/解码辅助
│       └── validators.py         # 验证器
│
├── mcp_server/                    # MCP服务器
│   ├── __init__.py
│   ├── server.py                 # MCP服务器主文件
│   ├── search_service.py         # 检索服务
│   └── protocol.py               # MCP协议实现
│
├── frontend/                      # React前端
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx               # 主应用组件 (含路由配置)
│   │   ├── index.jsx             # React入口文件 (含AuthProvider, Router)
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── context/              # React Context
│   │   │   └── AuthContext.jsx    # 认证Context
│   │   ├── pages/                # 页面级组件
│   │   │   ├── LoginPage.jsx
│   │   │   └── SignupPage.jsx
│   │   ├── components/           # React组件
│   │   │   ├── PromptList.jsx
│   │   │   ├── PromptEditor.jsx
│   │   │   ├── PromptSearch.jsx
│   │   │   ├── LLMOptimizer.jsx
│   │   │   ��── LoginForm.jsx
│   │   │   ├── SignupForm.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── services/             # API服务
│   │   │   └── api.js
│   │   ├── utils/                # 工具函数
│   │   │   └── helpers.js        # (假设已存在或按需创建)
│   └── public/
│
├── prompt-template/               # Prompt模板存储目录
│   └── .gitkeep
│
├── scripts/                       # 部署脚本
│   ├── install.sh
│   └── start.sh
│
└── tests/                         # 测试文件
    ├── test_backend.py
    └── test_mcp_server.py
```

## 访问系统

```txt
前端界面：http://localhost:3000
  - 登录页: http://localhost:3000/login
  - 注册页: http://localhost:3000/signup
后端API：http://localhost:8010
  - Auth API: http://localhost:8010/auth/...
  - Prompts API: http://localhost:8010/api/v1/prompts/... (部分受保护)
  - LLM API: http://localhost:8010/api/v1/llm/...
MCP Server：http://localhost:8011
```

## mcp配置

```json
{
  "mcpServers": {
    "prompt-management": {
      "url": "http://localhost:8011/mcp",
      "transport": "http"
    }
  }
}
```
