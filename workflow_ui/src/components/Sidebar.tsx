export default function Sidebar({ addNode }: any) {
    return (
      <div className="sidebar">
        <button onClick={() => addNode("prompt")}>➕ Prompt</button>
        <button onClick={() => addNode("terraform")}>➕ Terraform</button>
        <button onClick={() => addNode("llm")}>➕ LLM</button>
        <button onClick={() => addNode("filter")}>➕ Filter</button>
      </div>
    )
  }
  