#!/bin/bash

# 启动脚本 - 数据库模式
echo "🚀 Starting Prompt Management System with Database..."

# 检查环境变量
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set. Please configure your database connection."
    echo "Example: export DATABASE_URL='postgresql://user:password@localhost/prompt_management'"
    exit 1
fi

# 设置数据库模式
export USE_DATABASE=True

echo "📊 Database mode enabled"
echo "🔗 Database URL: $DATABASE_URL"

# 启动后端服务
echo "🔧 Starting backend server..."
cd "$(dirname "$0")/.."
uv run python -m uvicorn backend.main:app --host 0.0.0.0 --port 8010 --reload &
BACKEND_PID=$!

# 启动MCP服务器
echo "🔌 Starting MCP server..."
uv run python -m mcp_server.server &
MCP_PID=$!

echo "✅ Services started successfully!"
echo "📝 Backend API: http://localhost:8010"
echo "🔌 MCP Server: http://localhost:8011"
echo ""
echo "Press Ctrl+C to stop all services..."

# 等待中断信号
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $MCP_PID; exit 0' INT

# 保持脚本运行
wait