import { Handle, Position } from "reactflow"

export default function PromptNode({ data }: any) {
  return (
    <div className="node">
      <div className="node-title">Prompt</div>
      <textarea
        className="prompt-textarea"
        value={data.text || ""}
        onChange={e => data.onChange(e.target.value)}
        placeholder="Enter prompt..."
      />
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
