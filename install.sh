#!/bin/bash
# Auto-install script for LangChain Agent Platform

set -e

echo "🚀 LangChain Agent Platform - Auto Installer"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Clone repo
echo "📥 Cloning repository..."
git clone https://github.com/n00n0i/langchain-agent-platform.git /opt/langchain-agent-platform 2>/dev/null || true
cd /opt/langchain-agent-platform

# Configure
echo ""
echo "⚙️  Configuration"
echo "================"
read -p "OpenAI API Key (optional): " openai_key
read -p "Kimi API Key (optional): " kimi_key

cat > .env << EOF
OPENAI_API_KEY=${openai_key}
KIMI_API_KEY=${kimi_key}
EOF

# Start
echo ""
echo "🐳 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for startup..."
sleep 15

echo ""
echo "================================"
echo "✅ Installation Complete!"
echo "================================"
echo ""
echo "🌐 Access:"
echo "   Platform: http://localhost:3000"
echo "   API:      http://localhost:8000"
echo ""
echo "📁 Location: /opt/langchain-agent-platform"
echo ""
