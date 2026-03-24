import { Handle, Position } from "reactflow"

export default function LLMNode() {
  return (
    <div className="node">
      <div className="node-title">LLM</div>
      <div>Reasoning Node</div>
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
