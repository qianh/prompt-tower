#!/bin/bash

# 启动后端API服务器
echo "Starting backend API server..."
uv run python -m backend.main &
BACKEND_PID=$!

# 启动MCP服务器
echo "Starting MCP server..."
uv run python -m mcp_server.server &
MCP_PID=$!

# 启动前端开发服务器
echo "Starting frontend development server..."
cd frontend && npm start &
FRONTEND_PID=$!

echo "All services started!"
echo "Backend API: http://localhost:8010"
echo "MCP Server: http://localhost:8011"
echo "Frontend: http://localhost:3000"

# 等待退出信号
trap "kill $BACKEND_PID $MCP_PID $FRONTEND_PID" EXIT
wait
