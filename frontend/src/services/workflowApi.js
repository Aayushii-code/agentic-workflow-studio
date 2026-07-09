export function toWorkflowJSON(nodes, edges) {
  return {
    name: "Document Analysis Workflow",
    nodes: nodes.map((n) => ({
      id: n.id,
      type: n.type,
      position: n.position,
      config: n.data?.config || {},
    })),
    edges: edges.map((e) => ({
      source: e.source,
      target: e.target,
    })),
  };
}

export async function validateWorkflow(workflowJSON) {
  const res = await fetch("/api/workflows/validate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(workflowJSON),
  });

  if (!res.ok) {
    throw new Error("Workflow validation failed");
  }

  return await res.json();
}

export async function runWorkflow(workflowJSON) {
  const res = await fetch("/api/workflows/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(workflowJSON),
  });

  if (!res.ok) {
    throw new Error("Workflow execution failed");
  }

  return await res.json();
}