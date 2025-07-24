#!/bin/bash

# HistAgent Frontend 快速安装脚本

echo "🚀 开始安装 HistAgent Frontend..."

# 检查 Node.js 版本
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js (版本 >= 16)"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt "16" ]; then
    echo "❌ 错误: Node.js 版本过低 (当前: $(node -v))，请升级到 16+ 版本"
    exit 1
fi

echo "✅ Node.js 版本检查通过: $(node -v)"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到 npm"
    exit 1
fi

echo "✅ npm 版本: $(npm -v)"

# 安装依赖
echo "📦 安装项目依赖..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 检查 Tailwind CSS 是否需要额外配置
echo "🎨 配置 Tailwind CSS..."
if [ ! -f "node_modules/@tailwindcss/forms/package.json" ]; then
    npm install @tailwindcss/forms
fi

echo "✅ Tailwind CSS 配置完成"

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "⚙️ 创建环境配置文件..."
    cat > .env << EOL
# API 配置
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# 应用配置
VITE_APP_NAME=HistAgent
VITE_APP_VERSION=1.0.0

# 开发配置
VITE_DEV_PORT=3000
EOL
    echo "✅ 环境配置文件创建完成"
fi

# 运行类型检查
echo "🔍 运行类型检查..."
npm run type-check

if [ $? -ne 0 ]; then
    echo "⚠️ 类型检查发现问题，但安装继续进行"
fi

echo ""
echo "🎉 HistAgent Frontend 安装完成！"
echo ""
echo "📋 下一步操作:"
echo "   1. 启动开发服务器: npm run dev"
echo "   2. 访问应用: http://localhost:3000"
echo "   3. 确保后端服务运行在 http://localhost:8000"
echo ""
echo "📖 更多信息请查看 README.md"
echo "" 