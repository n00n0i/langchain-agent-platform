from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

class BaseAgent(ABC):
    """Base class สำหรับทุก Agents"""
    
    def __init__(
        self,
        id: str,
        name: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.agent_type = "base"
        self.model = model
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.team = None
        
        # Initialize LangChain LLM
        self.llm = ChatOpenAI(
            model_name=model,
            temperature=0.7
        )
    
    @abstractmethod
    def _default_system_prompt(self) -> str:
        """System prompt เริ่มต้นสำหรับ agent"""
        pass
    
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute task"""
        pass
    
    async def _call_llm(self, prompt: str) -> str:
        """เรียก LLM"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def get_from_memory(self, key: str) -> Any:
        """ดึงข้อมูลจาก shared memory"""
        if self.team:
            return self.team.shared_memory.get(key)
        return None
    
    def save_to_memory(self, key: str, value: Any):
        """บันทึกข้อมูลลง shared memory"""
        if self.team:
            self.team.shared_memory[key] = value
