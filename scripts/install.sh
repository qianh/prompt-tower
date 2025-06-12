#!/bin/bash

echo "Installing Prompt Management System..."

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 创建Python虚拟环境并安装依赖
echo "Setting up Python environment..."
uv venv
source .venv/bin/activate
uv pip install -e .

# 安装前端依赖
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# 创建环境变量文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please configure your API keys."
fi

# 创建prompt模板目录
mkdir -p prompt-template

echo "Installation complete!"
