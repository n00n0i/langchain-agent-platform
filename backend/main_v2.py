from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from agents.orchestrator import AgentOrchestrator
from agents.team import AgentTeam
from agents.agent_builder import agent_builder, CreateCustomAgentRequest, UpdateAgentRequest
from api.agent_builder_routes import router as agent_builder_router

load_dotenv()

app = FastAPI(
    title="LangChain Agent Platform",
    description="Multi-Agent Platform with Custom Agent Builder",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator
orchestrator = AgentOrchestrator()

# Include routers
app.include_router(agent_builder_router)

# Models
class CreateTeamRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    agents: List[str] = []  # Can be agent types or custom agent IDs
    use_custom_agents: bool = False

class ExecuteTaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = {}

# Routes
@app.get("/")
async def root():
    return {
        "name": "LangChain Agent Platform",
        "version": "2.0.0",
        "features": [
            "Multi-Agent Teams",
            "Custom Agent Builder",
            "LLM Configuration",
            "Skills & Tools",
            "Knowledge Bases"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "custom_agents": len(agent_builder.list_agents()),
        "templates": len(agent_builder.list_templates())
    }

# Team Management
@app.post("/teams")
async def create_team(request: CreateTeamRequest):
    """สร้างทีมใหม่"""
    try:
        if request.use_custom_agents:
            # Use custom agents
            team = orchestrator.create_team_with_custom_agents(
                name=request.name,
                description=request.description,
                agent_ids=request.agents
            )
        else:
            # Use built-in agent types
            team = orchestrator.create_team(
                name=request.name,
                description=request.description,
                agent_types=request.agents
            )
        
        return {
            "id": team.id,
            "name": team.name,
            "agents": [a.name for a in team.agents],
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/teams")
async def list_teams():
    """แสดงรายการทีมทั้งหมด"""
    teams = orchestrator.list_teams()
    return [{"id": t.id, "name": t.name, "agents": len(t.agents)} for t in teams]

@app.get("/teams/{team_id}")
async def get_team(team_id: str):
    """แสดงรายละเอียดทีม"""
    team = orchestrator.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "agents": [{"name": a.name, "type": a.agent_type} for a in team.agents],
        "status": team.status
    }

@app.delete("/teams/{team_id}")
async def delete_team(team_id: str):
    """ลบทีม"""
    success = orchestrator.delete_team(team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"status": "deleted"}

# Task Execution
@app.post("/teams/{team_id}/execute")
async def execute_task(team_id: str, request: ExecuteTaskRequest):
    """สั่งงานให้ทีมทำ"""
    team = orchestrator.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    result = await team.execute(request.task, request.context)
    return {
        "team_id": team_id,
        "task": request.task,
        "result": result,
        "status": "completed"
    }

# Agent Types
@app.get("/agent-types")
async def list_agent_types():
    """แสดงประเภท agent ที่มี"""
    return {
        "built_in": [
            {"id": "research", "name": "Research Agent", "description": "ค้นหาและรวบรวมข้อมูล"},
            {"id": "code", "name": "Code Agent", "description": "เขียนและตรวจสอบโค้ด"},
            {"id": "analysis", "name": "Analysis Agent", "description": "วิเคราะห์ข้อมูล"},
            {"id": "writing", "name": "Writing Agent", "description": "เขียนเอกสาร"},
            {"id": "review", "name": "Review Agent", "description": "ตรวจสอบคุณภาพ"}
        ],
        "custom": agent_builder.list_agents()
    }

# LLM Providers
@app.get("/llm-providers")
async def list_llm_providers():
    """แสดงรายการ LLM providers ที่รองรับ"""
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "requires_api_key": True
            },
            {
                "id": "kimi",
                "name": "Kimi (Moonshot)",
                "models": ["kimi-k2-0711-preview", "kimi-k2-0711"],
                "requires_api_key": True,
                "default_base_url": "https://api.moonshot.cn/v1"
            },
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "models": ["llama2", "codellama", "mistral"],
                "requires_api_key": False,
                "default_base_url": "http://localhost:11434"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
