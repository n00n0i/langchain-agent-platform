# LangChain Agent Platform

Multi-Agent Platform บน LangChain พร้อม Custom Agent Builder

## ✨ Features

### 🤖 Multi-Agent System
- สร้างทีม Agents หลายตัวทำงานร่วมกัน
- Task delegation และ coordination
- Shared memory ระหว่าง agents

### 🛠️ Custom Agent Builder
สร้าง Agent เองได้ด้วยการ configure:
- **LLM**: เลือก Provider (OpenAI, Kimi, Ollama) และ Model
- **Skills**: กำหนดความสามารถเฉพาะทาง
- **Knowledge**: เพิ่ม knowledge base สำหรับอ้างอิง
- **Tools**: เชื่อมต่อ tools ต่างๆ
- **System Prompt**: กำหนดบุคลิกและพฤติกรรม

### 📋 Pre-built Templates
- Developer Agent
- Research Agent
- Content Writer
- Data Analyst

## 🚀 Quick Start

### 1. ใช้ Auto-Install Script

```bash
curl -fsSL https://raw.githubusercontent.com/n00n0i/langchain-agent-platform/main/install.sh | bash
```

### 2. หรือ Manual Install

```bash
git clone https://github.com/n00n0i/langchain-agent-platform.git
cd langchain-agent-platform

# ตั้งค่า environment
cp .env.example .env
# แก้ไข .env ใส่ API Keys

# Start
docker-compose up -d
```

### 3. Access

- **Platform**: http://localhost:3000
- **API**: http://localhost:8000

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Platform                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   React     │◄──►│   FastAPI       │◄──►│   Custom    │ │
│  │   Frontend  │    │   Backend       │    │   Agents    │ │
│  │   :3000     │    │   :8000         │    │             │ │
│  └─────────────┘    └────────┬────────┘    └─────────────┘ │
│                               │                              │
│              ┌────────────────┼────────────────┐            │
│              │                │                │            │
│         ┌────┴────┐     ┌────┴────┐     ┌────┴────┐       │
│         │PostgreSQL│     │  Redis  │     │  LLM    │       │
│         │ :5432   │     │ :6379   │     │ APIs    │       │
│         └─────────┘     └─────────┘     └─────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📚 API Documentation

### Custom Agent Endpoints

```bash
# สร้าง custom agent
POST /agents/custom
{
  "name": "My Agent",
  "description": "Specialized agent",
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7
  },
  "skills": [
    {"name": "coding", "description": "Write code"}
  ],
  "knowledge_bases": [
    {"name": "docs", "content": "...", "type": "text"}
  ],
  "tools": [
    {"name": "search", "description": "Search web"}
  ]
}

# สร้างจาก template
POST /agents/custom/from-template/{template_name}

# ดูรายการ agents
GET /agents/custom

# สั่งงาน agent
POST /agents/custom/{agent_id}/execute
{
  "task": "เขียนโค้ด Python",
  "context": {}
}
```

### Team Endpoints

```bash
# สร้างทีม
POST /teams
{
  "name": "Dev Team",
  "agents": ["research", "code", "review"],
  "use_custom_agents": false
}

# สั่งงานทีม
POST /teams/{team_id}/execute
{
  "task": "สร้างระบบ login",
  "context": {}
}
```

## 🎨 Custom Agent Configuration

### LLM Providers

| Provider | Models | Requires API Key |
|:---|:---|:---:|
| OpenAI | gpt-4, gpt-3.5-turbo | ✅ |
| Kimi | kimi-k2-0711-preview | ✅ |
| Ollama | llama2, codellama | ❌ |

### Example: Create Custom Agent

```python
from agents.custom_agent import CustomAgent, LLMConfig, AgentSkill, AgentKnowledge

# สร้าง agent
agent = CustomAgent(
    name="Python Expert",
    description="Specialized in Python development",
    llm_config=LLMConfig(
        provider="openai",
        model="gpt-4",
        temperature=0.7
    ),
    skills=[
        AgentSkill(name="python", description="Write Python code"),
        AgentSkill(name="debugging", description="Debug code")
    ],
    knowledge_bases=[
        AgentKnowledge(
            name="python_best_practices",
            content="Python best practices...",
            type="text"
        )
    ]
)

# ใช้งาน
result = await agent.execute("เขียน function สำหรับจัดการ CSV")
```

## 🛠️ Development

### Backend

```bash
cd backend
pip install -r requirements.txt
python main_v2.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📝 Environment Variables

| Variable | Required | Description |
|:---|:---:|:---|
| `OPENAI_API_KEY` | ถ้าใช้ OpenAI | OpenAI API Key |
| `KIMI_API_KEY` | ถ้าใช้ Kimi | Kimi API Key |
| `DATABASE_URL` | No | PostgreSQL URL |
| `REDIS_URL` | No | Redis URL |

## 📁 Project Structure

```
langchain-agent-platform/
├── backend/
│   ├── agents/
│   │   ├── custom_agent.py       # Custom Agent หลัก
│   │   ├── agent_builder.py      # Agent Builder API
│   │   ├── base_agent.py         # Base class
│   │   ├── team.py               # Team management
│   │   ├── orchestrator.py       # Task orchestration
│   │   └── specialized_agents.py # Built-in agents
│   ├── api/
│   │   └── agent_builder_routes.py
│   ├── main_v2.py                # FastAPI app
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── components/
│           └── AgentBuilder.tsx  # UI สร้าง Agent
├── docker-compose.yml
└── README.md
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Submit PR

## 📄 License

MIT
