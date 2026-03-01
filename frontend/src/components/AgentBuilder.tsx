import { useState } from 'react'
import { Plus, Bot, Settings, Wrench, BookOpen, Brain } from 'lucide-react'

interface AgentBuilderProps {
  onCreateAgent: (agent: any) => void
}

function AgentBuilder({ onCreateAgent }: AgentBuilderProps) {
  const [step, setStep] = useState(1)
  const [agentConfig, setAgentConfig] = useState({
    name: '',
    description: '',
    llmProvider: 'openai',
    model: 'gpt-4',
    apiKey: '',
    temperature: 0.7,
    systemPrompt: '',
    skills: [] as { name: string; description: string }[],
    knowledgeBases: [] as { name: string; content: string }[],
    tools: [] as { name: string; description: string }[]
  })

  const [newSkill, setNewSkill] = useState({ name: '', description: '' })
  const [newKnowledge, setNewKnowledge] = useState({ name: '', content: '' })
  const [newTool, setNewTool] = useState({ name: '', description: '' })

  const llmProviders = [
    { id: 'openai', name: 'OpenAI', models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'] },
    { id: 'kimi', name: 'Kimi (Moonshot)', models: ['kimi-k2-0711-preview', 'kimi-k2-0711'] },
    { id: 'ollama', name: 'Ollama (Local)', models: ['llama2', 'codellama', 'mistral'] }
  ]

  const handleCreate = () => {
    onCreateAgent(agentConfig)
  }

  const addSkill = () => {
    if (newSkill.name && newSkill.description) {
      setAgentConfig({
        ...agentConfig,
        skills: [...agentConfig.skills, newSkill]
      })
      setNewSkill({ name: '', description: '' })
    }
  }

  const addKnowledge = () => {
    if (newKnowledge.name && newKnowledge.content) {
      setAgentConfig({
        ...agentConfig,
        knowledgeBases: [...agentConfig.knowledgeBases, newKnowledge]
      })
      setNewKnowledge({ name: '', content: '' })
    }
  }

  const addTool = () => {
    if (newTool.name && newTool.description) {
      setAgentConfig({
        ...agentConfig,
        tools: [...agentConfig.tools, newTool]
      })
      setNewTool({ name: '', description: '' })
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center gap-3 mb-6">
        <Bot className="w-8 h-8 text-blue-600" />
        <div>
          <h2 className="text-xl font-bold">Custom Agent Builder</h2>
          <p className="text-gray-500">สร้าง AI Agent ตามความต้องการ</p>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-4 mb-8">
        {[
          { num: 1, label: 'Basic', icon: Settings },
          { num: 2, label: 'LLM', icon: Brain },
          { num: 3, label: 'Skills', icon: Wrench },
          { num: 4, label: 'Knowledge', icon: BookOpen }
        ].map((s) => (
          <button
            key={s.num}
            onClick={() => setStep(s.num)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              step === s.num
                ? 'bg-blue-600 text-white'
                : step > s.num
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            <s.icon className="w-4 h-4" />
            <span className="text-sm">{s.label}</span>
          </button>
        ))}
      </div>

      {/* Step 1: Basic Info */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Agent Name</label>
            <input
              type="text"
              value={agentConfig.name}
              onChange={(e) => setAgentConfig({ ...agentConfig, name: e.target.value })}
              placeholder="เช่น My Developer Agent"
              className="w-full px-4 py-2 border rounded-lg focus:border-blue-600 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              value={agentConfig.description}
              onChange={(e) => setAgentConfig({ ...agentConfig, description: e.target.value })}
              placeholder="อธิบายว่า agent นี้ทำอะไร"
              rows={3}
              className="w-full px-4 py-2 border rounded-lg focus:border-blue-600 focus:outline-none"
            />
          </div>
          <button
            onClick={() => setStep(2)}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            ถัดไป
          </button>
        </div>
      )}

      {/* Step 2: LLM Configuration */}
      {step === 2 && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">LLM Provider</label>
            <select
              value={agentConfig.llmProvider}
              onChange={(e) => setAgentConfig({ ...agentConfig, llmProvider: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg focus:border-blue-600 focus:outline-none"
            >
              {llmProviders.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Model</label>
            <select
              value={agentConfig.model}
              onChange={(e) => setAgentConfig({ ...agentConfig, model: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg focus:border-blue-600 focus:outline-none"
            >
              {llmProviders
                .find((p) => p.id === agentConfig.llmProvider)
                ?.models.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">API Key (optional)</label>
            <input
              type="password"
              value={agentConfig.apiKey}
              onChange={(e) => setAgentConfig({ ...agentConfig, apiKey: e.target.value })}
              placeholder="ใส่ API Key ถ้าต้องการ override"
              className="w-full px-4 py-2 border rounded-lg focus:border-blue-600 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Temperature: {agentConfig.temperature}</label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={agentConfig.temperature}
              onChange={(e) => setAgentConfig({ ...agentConfig, temperature: parseFloat(e.target.value) })}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">System Prompt</label>
            <textarea
              value={agentConfig.systemPrompt}
              onChange={(e) => setAgentConfig({ ...agentConfig, systemPrompt: e.target.value })}
              placeholder="กำหนดบุคลิกและพฤติกรรมของ agent"
              rows={4}
              className="w-full px-4 py-2 border rounded-lg focus:border-blue-600 focus:outline-none"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50"
            >
              กลับ
            </button>
            <button
              onClick={() => setStep(3)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              ถัดไป
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Skills */}
      {step === 3 && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={newSkill.name}
              onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
              placeholder="ชื่อ skill"
              className="flex-1 px-4 py-2 border rounded-lg"
            />
            <input
              type="text"
              value={newSkill.description}
              onChange={(e) => setNewSkill({ ...newSkill, description: e.target.value })}
              placeholder="คำอธิบาย"
              className="flex-2 px-4 py-2 border rounded-lg"
            />
            <button
              onClick={addSkill}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>
          
          <div className="space-y-2">
            {agentConfig.skills.map((skill, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{skill.name}</p>
                  <p className="text-sm text-gray-500">{skill.description}</p>
                </div>
                <button
                  onClick={() => setAgentConfig({
                    ...agentConfig,
                    skills: agentConfig.skills.filter((_, i) => i !== idx)
                  })}
                  className="text-red-500 hover:text-red-700"
                >
                  ลบ
                </button>
              </div>
            ))}
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => setStep(2)}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50"
            >
              กลับ
            </button>
            <button
              onClick={() => setStep(4)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              ถัดไป
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Knowledge */}
      {step === 4 && (
        <div className="space-y-4">
          <div>
            <input
              type="text"
              value={newKnowledge.name}
              onChange={(e) => setNewKnowledge({ ...newKnowledge, name: e.target.value })}
              placeholder="ชื่อ knowledge base"
              className="w-full px-4 py-2 border rounded-lg mb-2"
            />
            <textarea
              value={newKnowledge.content}
              onChange={(e) => setNewKnowledge({ ...newKnowledge, content: e.target.value })}
              placeholder="เนื้อหาความรู้"
              rows={3}
              className="w-full px-4 py-2 border rounded-lg mb-2"
            />
            <button
              onClick={addKnowledge}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Plus className="w-5 h-5 inline mr-2" />
              เพิ่ม Knowledge
            </button>
          </div>
          
          <div className="space-y-2">
            {agentConfig.knowledgeBases.map((kb, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <p className="font-medium">{kb.name}</p>
                  <button
                    onClick={() => setAgentConfig({
                      ...agentConfig,
                      knowledgeBases: agentConfig.knowledgeBases.filter((_, i) => i !== idx)
                    })}
                    className="text-red-500 hover:text-red-700"
                  >
                    ลบ
                  </button>
                </div>
                <p className="text-sm text-gray-500 truncate">{kb.content}</p>
              </div>
            ))}
          </div>

          {/* Tools */}
          <div className="border-t pt-4">
            <h3 className="font-medium mb-3">Tools</h3>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={newTool.name}
                onChange={(e) => setNewTool({ ...newTool, name: e.target.value })}
                placeholder="ชื่อ tool"
                className="flex-1 px-4 py-2 border rounded-lg"
              />
              <input
                type="text"
                value={newTool.description}
                onChange={(e) => setNewTool({ ...newTool, description: e.target.value })}
                placeholder="คำอธิบาย"
                className="flex-2 px-4 py-2 border rounded-lg"
              />
              <button
                onClick={addTool}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-2">
              {agentConfig.tools.map((tool, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{tool.name}</p>
                    <p className="text-sm text-gray-500">{tool.description}</p>
                  </div>
                  <button
                    onClick={() => setAgentConfig({
                      ...agentConfig,
                      tools: agentConfig.tools.filter((_, i) => i !== idx)
                    })}
                    className="text-red-500 hover:text-red-700"
                  >
                    ลบ
                  </button>
                </div>
              ))}
            </div>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => setStep(3)}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50"
            >
              กลับ
            </button>
            <button
              onClick={handleCreate}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              สร้าง Agent
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentBuilder
