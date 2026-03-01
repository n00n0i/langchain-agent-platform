from typing import List, Dict, Any, Optional
from uuid import uuid4
import asyncio

from .team import AgentTeam
from .base_agent import BaseAgent
from models.database import TeamModel, TaskModel, db_session

class AgentOrchestrator:
    """Orchestrator สำหรับจัดการทีมและงาน"""
    
    def __init__(self):
        self.teams: Dict[str, AgentTeam] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._load_teams()
    
    def _load_teams(self):
        """โหลดทีมจาก database"""
        # Implementation สำหรับโหลดทีมที่มีอยู่
        pass
    
    def create_team(
        self,
        name: str,
        description: str = "",
        agent_types: List[str] = None
    ) -> AgentTeam:
        """สร้างทีมใหม่"""
        team_id = str(uuid4())
        
        team = AgentTeam(
            id=team_id,
            name=name,
            description=description
        )
        
        # เพิ่ม agents ตามประเภทที่ระบุ
        if agent_types:
            for agent_type in agent_types:
                team.add_agent(
                    name=f"{agent_type}_{team_id[:8]}",
                    agent_type=agent_type
                )
        
        self.teams[team_id] = team
        
        # บันทึกลง database
        self._save_team(team)
        
        return team
    
    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        """ดึงข้อมูลทีม"""
        return self.teams.get(team_id)
    
    def list_teams(self) -> List[AgentTeam]:
        """แสดงรายการทีมทั้งหมด"""
        return list(self.teams.values())
    
    def delete_team(self, team_id: str) -> bool:
        """ลบทีม"""
        if team_id in self.teams:
            del self.teams[team_id]
            self._delete_team_from_db(team_id)
            return True
        return False
    
    def create_task(
        self,
        team_id: str,
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """สร้างงานใหม่"""
        task_id = str(uuid4())
        
        self.tasks[task_id] = {
            "id": task_id,
            "team_id": team_id,
            "task": task,
            "context": context,
            "status": "queued",
            "result": None,
            "created_at": asyncio.get_event_loop().time()
        }
        
        # Queue task for execution
        asyncio.create_task(self._execute_task_async(task_id))
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลงาน"""
        return self.tasks.get(task_id)
    
    async def _execute_task_async(self, task_id: str):
        """Execute task in background"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task["status"] = "running"
        
        try:
            team = self.get_team(task["team_id"])
            if team:
                result = await team.execute(task["task"], task["context"])
                task["result"] = result
                task["status"] = "completed"
            else:
                task["status"] = "failed"
                task["error"] = "Team not found"
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
    
    def _save_team(self, team: AgentTeam):
        """บันทึกทีมลง database"""
        # Implementation สำหรับบันทึกทีม
        pass
    
    def _delete_team_from_db(self, team_id: str):
        """ลบทีมจาก database"""
        # Implementation สำหรับลบทีม
        pass
