import { Handle, Position } from "reactflow"

export default function ProviderNode({ data }: any) {
  return (
    <div className="node">
      <div className="node-title">Provider</div>
      <div>{data.provider}</div>
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
