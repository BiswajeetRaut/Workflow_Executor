import type { Node, Edge } from "reactflow"

export function serializeWorkflow(nodes: Node[], edges: Edge[]) {
  return {
    workflow: {
      nodes: nodes.map(n => ({
        id: n.id,
        type: n.type,
        data: n.data || {}
      })),
      edges: edges.map(e => ({
        from: e.source,
        to: e.target
      }))
    }
  }
}
