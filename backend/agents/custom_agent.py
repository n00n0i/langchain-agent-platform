from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from uuid import uuid4
import json

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.schema import SystemMessage, HumanMessage

@dataclass
class AgentSkill:
    """Skill ที่ agent สามารถใช้ได้"""
    name: str
    description: str
    function: Callable = None
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentKnowledge:
    """Knowledge base สำหรับ agent"""
    name: str
    content: str
    type: str = "text"  # text, json, markdown
    
@dataclass
class AgentTool:
    """Tool ที่ agent สามารถใช้ได้"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMConfig:
    """Configuration สำหรับ LLM"""
    provider: str = "openai"  # openai, kimi, ollama, anthropic
    model: str = "gpt-4"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    def create_llm(self):
        """สร้าง LLM instance"""
        if self.provider == "openai":
            return ChatOpenAI(
                model_name=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=self.api_key,
                base_url=self.api_base
            )
        elif self.provider == "kimi":
            return ChatOpenAI(
                model_name=self.model or "kimi-k2-0711-preview",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=self.api_key,
                base_url=self.api_base or "https://api.moonshot.cn/v1"
            )
        elif self.provider == "ollama":
            return Ollama(
                model=self.model or "llama2",
                base_url=self.api_base or "http://localhost:11434"
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

class CustomAgent:
    """Custom Agent ที่สามารถ configure ได้เต็มรูปแบบ"""
    
    def __init__(
        self,
        id: str = None,
        name: str = "Custom Agent",
        description: str = "",
        llm_config: LLMConfig = None,
        system_prompt: str = None,
        skills: List[AgentSkill] = None,
        knowledge_bases: List[AgentKnowledge] = None,
        tools: List[AgentTool] = None,
        memory_enabled: bool = True
    ):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description
        self.agent_type = "custom"
        
        # LLM Configuration
        self.llm_config = llm_config or LLMConfig()
        self.llm = self.llm_config.create_llm()
        
        # Prompt
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        # Capabilities
        self.skills = skills or []
        self.knowledge_bases = knowledge_bases or []
        self.tools = tools or []
        
        # Memory
        self.memory_enabled = memory_enabled
        self.memory: List[Dict[str, Any]] = []
        
        # Team reference
        self.team = None
    
    def _default_system_prompt(self) -> str:
        """สร้าง system prompt เริ่มต้น"""
        skills_desc = "\n".join([f"- {s.name}: {s.description}" for s in self.skills])
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        
        return f"""You are {self.name}, a specialized AI agent.
{self.description}

Your Skills:
{skills_desc or "- General problem solving"}

Available Tools:
{tools_desc or "- None"}

Guidelines:
1. Use your skills and tools effectively
2. Reference knowledge bases when relevant
3. Be thorough and accurate
4. Ask for clarification if needed
"""
    
    def add_skill(self, skill: AgentSkill):
        """เพิ่ม skill"""
        self.skills.append(skill)
        self._update_system_prompt()
    
    def add_knowledge(self, knowledge: AgentKnowledge):
        """เพิ่ม knowledge base"""
        self.knowledge_bases.append(knowledge)
    
    def add_tool(self, tool: AgentTool):
        """เพิ่ม tool"""
        self.tools.append(tool)
        self._update_system_prompt()
    
    def _update_system_prompt(self):
        """อัพเดท system prompt เมื่อมีการเปลี่ยนแปลง"""
        self.system_prompt = self._default_system_prompt()
    
    def _build_knowledge_context(self) -> str:
        """รวม knowledge bases เป็น context"""
        if not self.knowledge_bases:
            return ""
        
        context_parts = ["Knowledge Base:"]
        for kb in self.knowledge_bases:
            context_parts.append(f"\n### {kb.name}\n{kb.content[:2000]}")
        
        return "\n".join(context_parts)
    
    def _get_relevant_knowledge(self, query: str) -> str:
        """ค้นหา knowledge ที่เกี่ยวข้อง (simple keyword matching)"""
        relevant = []
        query_words = set(query.lower().split())
        
        for kb in self.knowledge_bases:
            kb_words = set(kb.content.lower().split())
            overlap = query_words & kb_words
            if len(overlap) > 0:
                relevant.append(kb.content[:1000])
        
        return "\n\n".join(relevant) if relevant else self._build_knowledge_context()
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute tool by name"""
        for tool in self.tools:
            if tool.name == tool_name:
                if tool.function:
                    return tool.function(**parameters)
                return {"error": f"Tool {tool_name} has no function"}
        return {"error": f"Tool {tool_name} not found"}
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute task with full capabilities"""
        
        # Build context
        knowledge_context = self._get_relevant_knowledge(task)
        shared_memory = self._get_shared_memory()
        
        # Build prompt
        prompt_parts = [f"Task: {task}"]
        
        if knowledge_context:
            prompt_parts.append(f"\nRelevant Knowledge:\n{knowledge_context}")
        
        if shared_memory:
            prompt_parts.append(f"\nShared Memory:\n{shared_memory}")
        
        if context:
            prompt_parts.append(f"\nAdditional Context:\n{json.dumps(context, indent=2)}")
        
        # Check if need to use tools
        tool_result = None
        if self.tools:
            tool_result = await self._decide_and_use_tools(task)
        
        if tool_result:
            prompt_parts.append(f"\nTool Results:\n{json.dumps(tool_result, indent=2)}")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Call LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        result_text = response.content
        
        # Save to memory
        if self.memory_enabled:
            self._save_to_memory(task, result_text)
        
        return {
            "agent": self.name,
            "type": self.agent_type,
            "task": task,
            "result": result_text,
            "tools_used": tool_result is not None,
            "knowledge_referenced": bool(knowledge_context),
            "summary": result_text[:200] + "..." if len(result_text) > 200 else result_text
        }
    
    async def _decide_and_use_tools(self, task: str) -> Optional[Dict[str, Any]]:
        """ตัดสินใจว่าควรใช้ tool ไหน"""
        # Simple implementation - ถ้ามี tool ที่ match keyword ให้ใช้
        tool_results = {}
        
        for tool in self.tools:
            if tool.name.lower() in task.lower():
                try:
                    result = tool.function()
                    tool_results[tool.name] = result
                except Exception as e:
                    tool_results[tool.name] = {"error": str(e)}
        
        return tool_results if tool_results else None
    
    def _get_shared_memory(self) -> str:
        """ดึงข้อมูลจาก shared memory"""
        if self.team and self.team.shared_memory:
            return json.dumps(self.team.shared_memory, indent=2)
        return ""
    
    def _save_to_memory(self, task: str, result: str):
        """บันทึกลง memory"""
        self.memory.append({
            "task": task,
            "result": result,
            "timestamp": str(uuid4())  # Should use proper timestamp
        })
        
        # Keep only last 10 memories
        if len(self.memory) > 10:
            self.memory = self.memory[-10:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type,
            "llm_config": {
                "provider": self.llm_config.provider,
                "model": self.llm_config.model,
                "temperature": self.llm_config.temperature,
                "max_tokens": self.llm_config.max_tokens
            },
            "system_prompt": self.system_prompt,
            "skills": [{"name": s.name, "description": s.description} for s in self.skills],
            "knowledge_bases": [{"name": k.name, "type": k.type} for k in self.knowledge_bases],
            "tools": [{"name": t.name, "description": t.description} for t in self.tools],
            "memory_enabled": self.memory_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomAgent':
        """Create from dictionary"""
        llm_config = LLMConfig(**data.get("llm_config", {}))
        
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description", ""),
            llm_config=llm_config,
            system_prompt=data.get("system_prompt"),
            memory_enabled=data.get("memory_enabled", True)
        )
