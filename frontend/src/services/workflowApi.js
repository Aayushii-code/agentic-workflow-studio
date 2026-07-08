export function toWorkflowJSON(nodes, edges) {
  return {
    workflow_id: crypto.randomUUID(),
    name: "Document Analysis Workflow",
    nodes: nodes.map(n => ({ id: n.id, type: n.type, position: n.position, config: n.data.config || {} })),
    edges: edges.map(e => ({ source: e.source, target: e.target })),
  };
}

export async function saveWorkflow(workflowJSON) {
  const res = await fetch('/api/workflows', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(workflowJSON) });
  return res.json();
}

export async function runWorkflow(workflowId) {
  const res = await fetch(`/api/workflows/${workflowId}/run`, { method: 'POST' });
  return res.json();
}