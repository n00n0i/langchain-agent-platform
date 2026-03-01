from typing import Dict, Any
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """Agent สำหรับค้นคว้าและรวบรวมข้อมูล"""
    
    agent_type = "research"
    
    def _default_system_prompt(self) -> str:
        return """You are a Research Agent specialized in gathering and analyzing information.
Your tasks include:
- Searching for relevant information
- Summarizing findings
- Identifying key insights
- Providing structured research results

Always provide comprehensive and well-organized research."""
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        prompt = f"""Research Task: {task}

Context: {context or 'No additional context'}

Please provide:
1. Key findings
2. Relevant information
3. Sources or references (if applicable)
4. Summary of research

Format your response in a structured way."""
        
        result = await self._call_llm(prompt)
        
        return {
            "agent": self.name,
            "type": self.agent_type,
            "task": task,
            "result": result,
            "summary": result[:200] + "..." if len(result) > 200 else result
        }


class CodeAgent(BaseAgent):
    """Agent สำหรับเขียนและตรวจสอบโค้ด"""
    
    agent_type = "code"
    
    def _default_system_prompt(self) -> str:
        return """You are a Code Agent specialized in software development.
Your tasks include:
- Writing clean, efficient code
- Debugging and fixing errors
- Code review and optimization
- Providing technical solutions

Always write production-ready code with proper documentation."""
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        research = self.get_from_memory("research_result")
        
        prompt = f"""Coding Task: {task}

Research Context: {research or 'No research available'}
Additional Context: {context or 'No additional context'}

Please provide:
1. Solution approach
2. Complete code implementation
3. Explanation of key parts
4. Usage examples

Use best practices and include comments."""
        
        result = await self._call_llm(prompt)
        
        return {
            "agent": self.name,
            "type": self.agent_type,
            "task": task,
            "result": result,
            "code": self._extract_code(result),
            "summary": "Code implementation provided"
        }
    
    def _extract_code(self, text: str) -> str:
        """Extract code blocks from response"""
        import re
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', text, re.DOTALL)
        return '\n\n'.join(code_blocks) if code_blocks else text


class AnalysisAgent(BaseAgent):
    """Agent สำหรับวิเคราะห์ข้อมูล"""
    
    agent_type = "analysis"
    
    def _default_system_prompt(self) -> str:
        return """You are an Analysis Agent specialized in data analysis and insights.
Your tasks include:
- Analyzing data patterns
- Creating reports
- Identifying trends
- Providing actionable insights

Always provide data-driven analysis with clear conclusions."""
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        prompt = f"""Analysis Task: {task}

Context: {context or 'No additional context'}

Please provide:
1. Data analysis
2. Key insights
3. Trends identified
4. Recommendations

Use structured format with clear sections."""
        
        result = await self._call_llm(prompt)
        
        return {
            "agent": self.name,
            "type": self.agent_type,
            "task": task,
            "result": result,
            "summary": "Analysis completed"
        }


class WritingAgent(BaseAgent):
    """Agent สำหรับเขียนเอกสาร"""
    
    agent_type = "writing"
    
    def _default_system_prompt(self) -> str:
        return """You are a Writing Agent specialized in content creation.
Your tasks include:
- Writing clear documentation
- Creating engaging content
- Editing and proofreading
- Translating content

Always produce high-quality, well-structured content."""
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        prompt = f"""Writing Task: {task}

Context: {context or 'No additional context'}

Please provide:
1. Well-structured content
2. Clear and engaging writing
3. Proper formatting
4. Final polished version

Adapt tone and style based on the task requirements."""
        
        result = await self._call_llm(prompt)
        
        return {
            "agent": self.name,
            "type": self.agent_type,
            "task": task,
            "result": result,
            "summary": "Content created"
        }


class ReviewAgent(BaseAgent):
    """Agent สำหรับตรวจสอบและให้ feedback"""
    
    agent_type = "review"
    
    def _default_system_prompt(self) -> str:
        return """You are a Review Agent specialized in quality assurance.
Your tasks include:
- Reviewing work for quality
- Providing constructive feedback
- Identifying issues
- Suggesting improvements

Always be thorough and constructive in your reviews."""
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        implementation = self.get_from_memory("implementation")
        
        prompt = f"""Review Task: {task}

Work to Review: {implementation or 'No implementation provided'}
Additional Context: {context or 'No additional context'}

Please provide:
1. Overall assessment
2. Strengths
3. Areas for improvement
4. Specific suggestions
5. Action items

Be constructive and specific."""
        
        result = await self._call_llm(prompt)
        
        return {
            "agent": self.name,
            "type": self.agent_type,
            "task": task,
            "result": result,
            "summary": "Review completed"
        }
