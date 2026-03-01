from typing import List, Dict, Any, Optional
from uuid import uuid4
import asyncio

from .base_agent import BaseAgent
from .specialized_agents import (
    ResearchAgent,
    CodeAgent,
    AnalysisAgent,
    WritingAgent,
    ReviewAgent
)

class AgentTeam:
    """ทีมของ Agents ที่ทำงานร่วมกัน"""
    
    AGENT_TYPE_MAP = {
        "research": ResearchAgent,
        "code": CodeAgent,
        "analysis": AnalysisAgent,
        "writing": WritingAgent,
        "review": ReviewAgent
    }
    
    def __init__(self, id: str, name: str, description: str = ""):
        self.id = id
        self.name = name
        self.description = description
        self.agents: List[BaseAgent] = []
        self.status = "idle"
        self.shared_memory: Dict[str, Any] = {}
    
    def add_agent(
        self,
        name: str,
        agent_type: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None
    ) -> BaseAgent:
        """เพิ่ม agent เข้าทีม"""
        agent_class = self.AGENT_TYPE_MAP.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent = agent_class(
            id=str(uuid4()),
            name=name,
            model=model,
            system_prompt=system_prompt
        )
        
        agent.team = self
        self.agents.append(agent)
        
        return agent
    
    def remove_agent(self, agent_id: str) -> bool:
        """ลบ agent ออกจากทีม"""
        for i, agent in enumerate(self.agents):
            if agent.id == agent_id:
                del self.agents[i]
                return True
        return False
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """สั่งงานให้ทีมทำ"""
        self.status = "working"
        
        try:
            # วิเคราะห์งานและกำหนดลำดับ
            execution_plan = self._create_execution_plan(task)
            
            results = []
            
            # ทำงานตามลำดับ
            for step in execution_plan:
                agent = self._get_agent_for_task(step["agent_type"])
                if agent:
                    result = await agent.execute(
                        task=step["task"],
                        context={**step.get("context", {}), **(context or {})}
                    )
                    results.append({
                        "agent": agent.name,
                        "type": agent.agent_type,
                        "result": result
                    })
                    
                    # บันทึกลง shared memory
                    self.shared_memory[step["id"]] = result
            
            # รวมผลลัพธ์
            final_result = self._aggregate_results(results, task)
            
            self.status = "idle"
            return final_result
            
        except Exception as e:
            self.status = "error"
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def _create_execution_plan(self, task: str) -> List[Dict[str, Any]]:
        """สร้างแผนการทำงานจาก task"""
        # Simple planning - แบ่งงานตามประเภท agents ที่มี
        plan = []
        
        # ถ้ามี research agent ให้เริ่มจากการ research
        if any(a.agent_type == "research" for a in self.agents):
            plan.append({
                "id": f"step_{len(plan)}",
                "agent_type": "research",
                "task": f"Research information for: {task}",
                "context": {}
            })
        
        # ถ้ามี code agent ให้ทำการ implement
        if any(a.agent_type == "code" for a in self.agents):
            plan.append({
                "id": f"step_{len(plan)}",
                "agent_type": "code",
                "task": f"Implement solution for: {task}",
                "context": {"research_result": "previous_step"}
            })
        
        # ถ้ามี review agent ให้ตรวจสอบ
        if any(a.agent_type == "review" for a in self.agents):
            plan.append({
                "id": f"step_{len(plan)}",
                "agent_type": "review",
                "task": f"Review and provide feedback on: {task}",
                "context": {"implementation": "previous_step"}
            })
        
        return plan
    
    def _get_agent_for_task(self, agent_type: str) -> Optional[BaseAgent]:
        """หา agent ที่เหมาะสมสำหรับงาน"""
        for agent in self.agents:
            if agent.agent_type == agent_type:
                return agent
        return None
    
    def _aggregate_results(self, results: List[Dict[str, Any]], original_task: str) -> Dict[str, Any]:
        """รวมผลลัพธ์จากทุก agents"""
        return {
            "task": original_task,
            "status": "completed",
            "steps": len(results),
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """สร้างสรุปจากผลลัพธ์"""
        summaries = []
        for r in results:
            if isinstance(r.get("result"), dict) and "summary" in r["result"]:
                summaries.append(r["result"]["summary"])
        
        return "\n".join(summaries) if summaries else "Task completed successfully"
