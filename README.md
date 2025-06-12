# Prompt管理系统

一个基于Python和React的Prompt管理系统，支持MCP Server协议，提供完整的prompt管理功能和LLM优化能力。

## 功能特性

### 网页部分

- ✅ **基础管理功能**：查询、复制、编辑、启用/禁用prompt
- ✅ **智能搜索**：支持按标题、标签、内容关键词搜索
- ✅ **LLM优化**：集成Gemini、Qwen、DeepSeek等LLM，自动优化prompt
- ✅ **实时同步**：所有生效的prompt自动同步到MCP Server

### MCP Server

- ✅ **标准协议**：支持Streamablehttp协议调用
- ✅ **高效检索**：按优先级（标题>标签>内容）检索prompt
- ✅ **批量输出**：支持多结果列表输出
- ✅ **实时更新**：自动加载最新的prompt模板

## 技术栈

- **后端**：Python 3.11+, FastAPI, uv
- **前端**：React 18, Ant Design 5
- **LLM支持**：Gemini, Qwen, DeepSeek
- **协议**：MCP (Model Context Protocol)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/prompt-management-system.git
cd prompt-management-system
```

## 整体架构图

```txt
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器                              │
│                   React Frontend                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  查询 | 复制 | 编辑 | 启用/禁用 | LLM优化          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────┴───────────────────────────────────────┐
│                  Python Backend (FastAPI)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Prompt管理API | LLM集成 | 文件存储管理            │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌───────────────────────┴─────────────────────────────┐   │
│  │           prompt-template/目录                       │   │
│  │         (YAML格式的prompt文件存储)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 共享数据
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
│   ├── api/                      # API路由
│   │   ├── __init__.py
│   │   ├── prompts.py           # Prompt管理API
│   │   └── llm.py               # LLM相关API
│   ├── services/                 # 业务逻辑
│   │   ├── __init__.py
│   │   ├── prompt_service.py    # Prompt管理服务
│   │   ├── llm_service.py       # LLM服务
│   │   └── file_service.py      # 文件管理服务
│   └── utils/                    # 工具函数
│       ├── __init__.py
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
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── components/           # React组件
│   │   │   ├── PromptList.js
│   │   │   ├── PromptEditor.js
│   │   │   ├── PromptSearch.js
│   │   │   └── LLMOptimizer.js
│   │   ├── services/             # API服务
│   │   │   └── api.js
│   │   └── utils/                # 工具函数
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
后端API：http://localhost:8000
MCP Server：http://localhost:8001
```

## mcp配置

```json
{
  "mcpServers": {
    "prompt-management": {
      "url": "http://localhost:8001/mcp",
      "transport": "http"
    }
  }
}
```
