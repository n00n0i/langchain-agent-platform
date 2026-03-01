from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from agents.custom_agent import CustomAgent, LLMConfig, AgentSkill, AgentKnowledge, AgentTool
from agents.team import AgentTeam

class CreateCustomAgentRequest(BaseModel):
    """Request model for creating custom agent"""
    name: str
    description: str = ""
    llm_config: Dict[str, Any] = {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7
    }
    system_prompt: Optional[str] = None
    skills: List[Dict[str, str]] = []
    knowledge_bases: List[Dict[str, str]] = []
    tools: List[Dict[str, str]] = []
    memory_enabled: bool = True

class UpdateAgentRequest(BaseModel):
    """Request model for updating agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    llm_config: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    skills: Optional[List[Dict[str, str]]] = None
    knowledge_bases: Optional[List[Dict[str, str]]] = None
    tools: Optional[List[Dict[str, str]]] = None
    memory_enabled: Optional[bool] = None

class AgentBuilderAPI:
    """API สำหรับสร้างและจัดการ Custom Agents"""
    
    def __init__(self):
        self.custom_agents: Dict[str, CustomAgent] = {}
        self.agent_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """โหลด templates สำหรับ agents"""
        return {
            "developer": {
                "name": "Developer Agent",
                "description": "Specialized in software development",
                "skills": [
                    {"name": "code_writing", "description": "Write clean, efficient code"},
                    {"name": "debugging", "description": "Debug and fix errors"},
                    {"name": "code_review", "description": "Review code for quality"}
                ],
                "system_prompt": """You are an expert software developer.
Your expertise includes:
- Writing clean, maintainable code
- Debugging complex issues
- Following best practices
- Providing code reviews

Always write production-ready code with proper documentation."""
            },
            "researcher": {
                "name": "Research Agent",
                "description": "Specialized in research and analysis",
                "skills": [
                    {"name": "web_search", "description": "Search for information online"},
                    {"name": "data_analysis", "description": "Analyze research data"},
                    {"name": "summarization", "description": "Summarize findings"}
                ],
                "system_prompt": """You are a research specialist.
Your capabilities include:
- Finding relevant information
- Analyzing data objectively
- Summarizing complex topics
- Citing sources properly

Always provide well-researched, accurate information."""
            },
            "writer": {
                "name": "Content Writer",
                "description": "Specialized in content creation",
                "skills": [
                    {"name": "content_writing", "description": "Write engaging content"},
                    {"name": "editing", "description": "Edit and proofread"},
                    {"name": "seo", "description": "Optimize for SEO"}
                ],
                "system_prompt": """You are a professional content writer.
Your skills include:
- Writing engaging, clear content
- Adapting tone for different audiences
- SEO optimization
- Editing and proofreading

Always produce high-quality, engaging content."""
            },
            "analyst": {
                "name": "Data Analyst",
                "description": "Specialized in data analysis",
                "skills": [
                    {"name": "data_processing", "description": "Process and clean data"},
                    {"name": "visualization", "description": "Create visualizations"},
                    {"name": "reporting", "description": "Generate reports"}
                ],
                "system_prompt": """You are a data analysis expert.
Your expertise includes:
- Data processing and cleaning
- Statistical analysis
- Data visualization
- Insight generation

Always provide data-driven insights with clear explanations."""
            }
        }
    
    def create_agent(self, request: CreateCustomAgentRequest) -> CustomAgent:
        """สร้าง custom agent ใหม่"""
        
        # Create LLM Config
        llm_config = LLMConfig(**request.llm_config)
        
        # Create Skills
        skills = [
            AgentSkill(name=s["name"], description=s["description"])
            for s in request.skills
        ]
        
        # Create Knowledge Bases
        knowledge_bases = [
            AgentKnowledge(
                name=k["name"],
                content=k.get("content", ""),
                type=k.get("type", "text")
            )
            for k in request.knowledge_bases
        ]
        
        # Create Tools (will be bound later)
        tools = [
            AgentTool(name=t["name"], description=t["description"], function=None)
            for t in request.tools
        ]
        
        # Create Agent
        agent = CustomAgent(
            name=request.name,
            description=request.description,
            llm_config=llm_config,
            system_prompt=request.system_prompt,
            skills=skills,
            knowledge_bases=knowledge_bases,
            tools=tools,
            memory_enabled=request.memory_enabled
        )
        
        self.custom_agents[agent.id] = agent
        return agent
    
    def create_from_template(self, template_name: str, custom_name: str = None) -> CustomAgent:
        """สร้าง agent จาก template"""
        template = self.agent_templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        request = CreateCustomAgentRequest(
            name=custom_name or template["name"],
            description=template.get("description", ""),
            skills=template.get("skills", []),
            system_prompt=template.get("system_prompt")
        )
        
        return self.create_agent(request)
    
    def get_agent(self, agent_id: str) -> Optional[CustomAgent]:
        """ดึง agent ตาม ID"""
        return self.custom_agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """แสดงรายการ agents ทั้งหมด"""
        return [agent.to_dict() for agent in self.custom_agents.values()]
    
    def update_agent(self, agent_id: str, request: UpdateAgentRequest) -> Optional[CustomAgent]:
        """อัพเดท agent"""
        agent = self.custom_agents.get(agent_id)
        if not agent:
            return None
        
        if request.name:
            agent.name = request.name
        if request.description:
            agent.description = request.description
        if request.system_prompt:
            agent.system_prompt = request.system_prompt
        if request.memory_enabled is not None:
            agent.memory_enabled = request.memory_enabled
        if request.llm_config:
            agent.llm_config = LLMConfig(**request.llm_config)
            agent.llm = agent.llm_config.create_llm()
        
        return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """ลบ agent"""
        if agent_id in self.custom_agents:
            del self.custom_agents[agent_id]
            return True
        return False
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """แสดงรายการ templates"""
        return [
            {
                "id": key,
                "name": value["name"],
                "description": value["description"],
                "skills_count": len(value.get("skills", []))
            }
            for key, value in self.agent_templates.items()
        ]
    
    def add_skill_to_agent(self, agent_id: str, skill: Dict[str, str]) -> bool:
        """เพิ่ม skill ให้ agent"""
        agent = self.custom_agents.get(agent_id)
        if not agent:
            return False
        
        agent.add_skill(AgentSkill(
            name=skill["name"],
            description=skill["description"]
        ))
        return True
    
    def add_knowledge_to_agent(self, agent_id: str, knowledge: Dict[str, str]) -> bool:
        """เพิ่ม knowledge base ให้ agent"""
        agent = self.custom_agents.get(agent_id)
        if not agent:
            return False
        
        agent.add_knowledge(AgentKnowledge(
            name=knowledge["name"],
            content=knowledge.get("content", ""),
            type=knowledge.get("type", "text")
        ))
        return True
    
    def add_tool_to_agent(self, agent_id: str, tool: Dict[str, Any]) -> bool:
        """เพิ่ม tool ให้ agent"""
        agent = self.custom_agents.get(agent_id)
        if not agent:
            return False
        
        # Note: Tools with functions need to be bound separately
        agent.add_tool(AgentTool(
            name=tool["name"],
            description=tool["description"],
            function=None  # Function needs to be bound separately
        ))
        return True

# Global instance
agent_builder = AgentBuilderAPI()
