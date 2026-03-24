import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge
} from "reactflow"
import "reactflow/dist/style.css"
import { useState } from "react"
import { v4 as uuid } from "uuid"

import PromptNode from "./components/nodes/PromptNode"
import ProviderNode from "./components/nodes/ProviderNode"
import LLMNode from "./components/nodes/LLMNode"
import FilterNode from "./components/nodes/FilterNode"
import Sidebar from "./components/Sidebar"
import OutputPanel from "./components/OutputPanel"

import { serializeWorkflow } from "./utils/serializer"
import { verifyWorkflow, runWorkflow } from "./api/workflow"

import "./styles.css"

const nodeTypes = {
  prompt: PromptNode,
  terraform: ProviderNode,
  github: ProviderNode,
  confluence: ProviderNode,
  llm: LLMNode,
  filter: FilterNode
}

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [verifyResult, setVerifyResult] = useState<any>(null)
  const [runResult, setRunResult] = useState<any>(null)

  function addNode(type: string) {
    const id = uuid()
    setNodes(n => [
      ...n,
      {
        id,
        type,
        position: { x: 100, y: 100 + n.length * 90 },
        data:
          type === "prompt"
            ? {
                text: "",
                onChange: (text: string) => {
                  setNodes(ns =>
                    ns.map(node =>
                      node.id === id
                        ? { ...node, data: { ...node.data, text } }
                        : node
                    )
                  )
                }
              }
            : { provider: type }
      }
    ])
  }

  async function handleVerify() {
    const payload = serializeWorkflow(nodes, edges)
    const res = await verifyWorkflow(payload)
    setVerifyResult(res)
    setRunResult(null)
  }

  async function handleRun() {
    const res = await runWorkflow(verifyResult.execution_plan)
    setRunResult(res)
  }

  return (
    <div className="app">
      <Sidebar addNode={addNode} />

      <div className="canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={params => setEdges(e => addEdge(params, e))}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>

        <div className="controls">
          <button onClick={handleVerify}>Validate</button>
          <button onClick={handleRun} disabled={!verifyResult}>
            Run
          </button>
        </div>

        <OutputPanel
          verifyResult={verifyResult}
          runResult={runResult}
        />
      </div>
    </div>
  )
}
