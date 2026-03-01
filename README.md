# LangChain Agent Platform - Production Ready

Multi-Agent Platform with Custom Agent Builder on LangChain. **Production-ready** with enterprise-grade orchestration and monitoring.

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     React Frontend (TypeScript)                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │    │
│  │  │   Agent     │  │    Team     │  │   Task      │  │ Dashboard│   │    │
│  │  │   Builder   │  │  Management │  │   Queue     │  │ (Metrics)│   │    │
│  │  │  ┌───────┐  │  │  ┌───────┐  │  │  ┌───────┐  │  │  ┌────┐  │   │    │
│  │  │  │Create │  │  │  │Create │  │  │  │Submit │  │  │  │View│  │   │    │
│  │  │  │Custom │  │  │  │Team   │  │  │  │Task   │  │  │  │Stats│  │   │    │
│  │  │  │Agent  │  │  │  │       │  │  │  │       │  │  │  │     │  │   │    │
│  │  │  └───────┘  │  │  └───────┘  │  │  └───────┘  │  │  └────┘  │   │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ HTTPS / WebSocket
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (Nginx)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  SSL/TLS    │  │ Rate Limit  │  │   Auth      │  │   Load Balancing    │ │
│  │ Termination │  │  (Req/s)    │  │  (JWT)      │  │   (Round Robin)     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND (Python)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         REST API Layer                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │    │
│  │  │  /agents    │  │   /teams    │  │   /tasks    │  │  /auth   │   │    │
│  │  │  (CRUD)     │  │  (Manage)   │  │  (Execute)  │  │ (Login)  │   │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬─────┘   │    │
│  │         └─────────────────┴─────────────────┴──────────────┘         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐   │
│  │                    Agent Orchestrator (LangChain)                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐    │   │
│  │  │   Task      │  │   Agent     │  │   Result    │  │  Shared  │    │   │
│  │  │   Queue     │  │   Router    │  │  Aggregator │  │  Memory  │    │   │
│  │  │  (Celery)   │  │             │  │             │  │          │    │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬─────┘    │   │
│  │         └─────────────────┴─────────────────┴──────────────┘          │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐   │
│  │                    Agent Execution Layer                               │   │
│  │                                                                        │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │  Research Agent │  │   Code Agent    │  │ Analysis Agent  │        │   │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │        │   │
│  │  │  │  Search   │  │  │  │  Write    │  │  │  │  Analyze  │  │        │   │
│  │  │  │  Summarize│  │  │  │  Debug    │  │  │  │  Report   │  │        │   │
│  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  │                                                                        │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │  Writing Agent  │  │  Review Agent   │  │  Custom Agent   │        │   │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │        │   │
│  │  │  │  Create   │  │  │  │  Review   │  │  │  │  Config   │  │        │   │
│  │  │  │  Edit     │  │  │  │  Feedback │  │  │  │  Skills   │  │        │   │
│  │  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  │                                                                        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
└────────────────────────────────────┼──────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER (Docker)                               │
│                                                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐               │
│  │   PostgreSQL    │  │     Redis       │  │  Celery Worker  │               │
│  │   (Database)    │  │   (Cache/Queue) │  │  (Background)   │               │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │               │
│  │  │  Users    │  │  │  │  Session  │  │  │  │  Process  │  │               │
│  │  │  Agents   │  │  │  │  Queue    │  │  │  │  Tasks    │  │               │
│  │  │  Teams    │  │  │  │  Pub/Sub  │  │  │  │  Async    │  │               │
│  │  │  Tasks    │  │  │  └───────────┘  │  │  └───────────┘  │               │
│  │  └───────────┘  │  └─────────────────┘  └─────────────────┘               │
│  └─────────────────┘                                                          │
│                                                                                │
│  ┌─────────────────┐  ┌─────────────────┐                                     │
│  │   Prometheus    │  │     Grafana     │                                     │
│  │   (Metrics)     │  │   (Dashboard)   │                                     │
│  │                 │  │                 │                                     │
│  │  - API Latency  │  │  - Agent Stats  │                                     │
│  │  - Task Queue   │  │  - Task Queue   │                                     │
│  │  - Error Rate   │  │  - System Health│                                     │
│  └─────────────────┘  └─────────────────┘                                     │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Agent Creation Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│ Configure│────▶│ Validate│────▶│  Create │
│ Request │     │  Agent   │     │  Config │     │  Agent  │
│         │     │         │     │         │     │  Object │
└─────────┘     └────┬────┘     └─────────┘     └────┬────┘
                     │                                │
        ┌────────────┼────────────────────────────────┘
        │            │
        ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Select    │ │   Define    │ │   Attach    │
│   LLM       │ │   Skills    │ │  Knowledge  │
│  Provider   │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Task Execution Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Submit │────▶│  Parse  │────▶│  Route  │────▶│  Queue  │
│  Task   │     │  Task   │     │  to     │     │  Task   │
│         │     │         │     │  Team   │     │         │
└─────────┘     └─────────┘     └────┬────┘     └────┬────┘
                                     │               │
                              ┌──────┘               │
                              ▼                      ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Return │◀────│ Aggregate│◀────│  Agent  │◀────│  Worker │
│  Result │     │  Results │     │ Execute │     │  Pickup │
│         │     │          │     │         │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### Multi-Agent Collaboration Flow

```
┌─────────────┐
│   Team      │
│  Coordinator│
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           Task Decomposition             │
│  ┌─────────┬─────────┬─────────┐       │
│  │ Subtask │ Subtask │ Subtask │       │
│  │    1    │    2    │    3    │       │
│  └────┬────┴────┬────┴────┬────┘       │
└───────┼─────────┼─────────┼────────────┘
        │         │         │
        ▼         ▼         ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Research│ │  Code  │ │ Review │
   │ Agent  │ │ Agent  │ │ Agent  │
   └───┬────┘ └───┬────┘ └───┬────┘
       │         │         │
       └─────────┼─────────┘
                 ▼
          ┌────────────┐
          │   Shared   │
          │   Memory   │
          └──────┬─────┘
                 │
                 ▼
          ┌────────────┐
          │  Aggregate │
          │   Result   │
          └────────────┘
```

### Custom Agent Configuration Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Select    │────▶│  Configure  │────▶│   Attach    │
│  Template   │     │    LLM      │     │   Skills    │
│  (Optional) │     │  Provider   │     │             │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   Model     │     │   Tools     │
                    │ Temperature │     │             │
                    │ Max Tokens  │     │             │
                    └──────┬──────┘     └──────┬──────┘
                           │                    │
                           └────────┬───────────┘
                                    ▼
                           ┌─────────────┐
                           │   Add       │
                           │  Knowledge  │
                           │   Bases     │
                           └──────┬──────┘
                                  │
                                  ▼
                           ┌─────────────┐
                           │   Deploy    │
                           │   Agent     │
                           └─────────────┘
```

## 🚀 Quick Start

### Production Install

```bash
curl -fsSL https://raw.githubusercontent.com/n00n0i/langchain-agent-platform/main/install-production.sh | sudo bash
```

### Manual Install

```bash
# 1. Clone
git clone https://github.com/n00n0i/langchain-agent-platform.git
cd langchain-agent-platform

# 2. Configure
cp .env.production.example .env.production
# Edit with your API keys

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

Access dashboards:
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090
- **API Docs**: http://localhost:8000/docs

## 🔒 Security

- JWT Authentication
- Role-based access control
- API rate limiting
- Input validation
- Audit logging

## 📄 License

MIT
