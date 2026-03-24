import { Handle, Position } from "reactflow"

export default function FilterNode() {
  return (
    <div className="node">
      <div className="node-title">Filter</div>
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
