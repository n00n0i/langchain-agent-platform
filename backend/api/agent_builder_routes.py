from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from agents.agent_builder import (
    agent_builder,
    CreateCustomAgentRequest,
    UpdateAgentRequest
)

router = APIRouter(prefix="/agents", tags=["Custom Agents"])

@router.post("/custom")
async def create_custom_agent(request: CreateCustomAgentRequest):
    """สร้าง custom agent ใหม่"""
    try:
        agent = agent_builder.create_agent(request)
        return {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/custom/from-template/{template_name}")
async def create_agent_from_template(template_name: str, custom_name: str = None):
    """สร้าง agent จาก template"""
    try:
        agent = agent_builder.create_from_template(template_name, custom_name)
        return {
            "id": agent.id,
            "name": agent.name,
            "template": template_name,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/custom")
async def list_custom_agents():
    """แสดงรายการ custom agents ทั้งหมด"""
    return agent_builder.list_agents()

@router.get("/custom/{agent_id}")
async def get_custom_agent(agent_id: str):
    """ดึงข้อมูล custom agent"""
    agent = agent_builder.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()

@router.put("/custom/{agent_id}")
async def update_custom_agent(agent_id: str, request: UpdateAgentRequest):
    """อัพเดท custom agent"""
    agent = agent_builder.update_agent(agent_id, request)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "id": agent.id,
        "name": agent.name,
        "status": "updated"
    }

@router.delete("/custom/{agent_id}")
async def delete_custom_agent(agent_id: str):
    """ลบ custom agent"""
    success = agent_builder.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "deleted"}

@router.get("/templates")
async def list_agent_templates():
    """แสดงรายการ agent templates"""
    return agent_builder.list_templates()

@router.get("/templates/{template_name}")
async def get_agent_template(template_name: str):
    """ดึงข้อมูล template"""
    templates = agent_builder.agent_templates
    if template_name not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    return templates[template_name]

# Skills Management
@router.post("/custom/{agent_id}/skills")
async def add_skill_to_agent(agent_id: str, skill: Dict[str, str]):
    """เพิ่ม skill ให้ agent"""
    success = agent_builder.add_skill_to_agent(agent_id, skill)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "skill added"}

# Knowledge Management
@router.post("/custom/{agent_id}/knowledge")
async def add_knowledge_to_agent(agent_id: str, knowledge: Dict[str, str]):
    """เพิ่ม knowledge base ให้ agent"""
    success = agent_builder.add_knowledge_to_agent(agent_id, knowledge)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "knowledge added"}

# Tools Management
@router.post("/custom/{agent_id}/tools")
async def add_tool_to_agent(agent_id: str, tool: Dict[str, Any]):
    """เพิ่ม tool ให้ agent"""
    success = agent_builder.add_tool_to_agent(agent_id, tool)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "tool added"}

# Execute custom agent
@router.post("/custom/{agent_id}/execute")
async def execute_custom_agent(agent_id: str, task: Dict[str, str]):
    """สั่งงาน custom agent"""
    agent = agent_builder.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    import asyncio
    result = await agent.execute(
        task=task.get("task", ""),
        context=task.get("context", {})
    )
    return result
