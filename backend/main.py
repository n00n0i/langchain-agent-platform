from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from agents.orchestrator import AgentOrchestrator
from agents.team import AgentTeam
from models.database import init_db

load_dotenv()

app = FastAPI(
    title="LangChain Agent Platform",
    description="Multi-Agent Platform for team collaboration",
    version="1.0.0"
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

# Models
class CreateTeamRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    agents: List[str] = []

class ExecuteTaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = {}

class AgentConfig(BaseModel):
    name: str
    agent_type: str
    model: Optional[str] = "gpt-4"
    system_prompt: Optional[str] = None

# Routes
@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {
        "name": "LangChain Agent Platform",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Team Management
@app.post("/teams")
async def create_team(request: CreateTeamRequest):
    """สร้างทีมใหม่"""
    try:
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
    teams = orchestrstrator.list_teams()
    return [{"id": t.id, "name": t.name, "agents": len(t.agents)} for t in teams]

@app.get("/teams/{team_id}")
async def get_team(team_id: str):
    """แสดงรายละเอียดทีม"""
    team = orchestrstrator.get_team(team_id)
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
    success = orchestrstrator.delete_team(team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"status": "deleted"}

# Task Execution
@app.post("/teams/{team_id}/execute")
async def execute_task(team_id: str, request: ExecuteTaskRequest, background_tasks: BackgroundTasks):
    """สั่งงานให้ทีมทำ"""
    team = orchestrstrator.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Execute task
    result = await team.execute(request.task, request.context)
    return {
        "team_id": team_id,
        "task": request.task,
        "result": result,
        "status": "completed"
    }

@app.post("/teams/{team_id}/execute/async")
async def execute_task_async(team_id: str, request: ExecuteTaskRequest, background_tasks: BackgroundTasks):
    """สั่งงานแบบ async (background)"""
    team = orchestrstrator.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    task_id = orchestrstrator.create_task(team_id, request.task, request.context)
    
    return {
        "task_id": task_id,
        "team_id": team_id,
        "task": request.task,
        "status": "queued"
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """ตรวจสอบสถานะงาน"""
    task = orchestrstrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Agent Management
@app.post("/teams/{team_id}/agents")
async def add_agent(team_id: str, config: AgentConfig):
    """เพิ่ม agent เข้าทีม"""
    team = orchestrstrator.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    agent = team.add_agent(
        name=config.name,
        agent_type=config.agent_type,
        model=config.model,
        system_prompt=config.system_prompt
    )
    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.agent_type,
        "status": "added"
    }

@app.get("/agent-types")
async def list_agent_types():
    """แสดงประเภท agent ที่มี"""
    return {
        "types": [
            {
                "id": "research",
                "name": "Research Agent",
                "description": "ค้นหาและรวบรวมข้อมูล",
                "capabilities": ["search", "summarize", "analyze"]
            },
            {
                "id": "code",
                "name": "Code Agent",
                "description": "เขียนและตรวจสอบโค้ด",
                "capabilities": ["write_code", "debug", "review"]
            },
            {
                "id": "analysis",
                "name": "Analysis Agent",
                "description": "วิเคราะห์ข้อมูลและสร้าง report",
                "capabilities": ["analyze", "report", "visualize"]
            },
            {
                "id": "writing",
                "name": "Writing Agent",
                "description": "เขียนเอกสารและ content",
                "capabilities": ["write", "edit", "translate"]
            },
            {
                "id": "review",
                "name": "Review Agent",
                "description": "ตรวจสอบคุณภาพและให้ feedback",
                "capabilities": ["review", "feedback", "suggest"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
