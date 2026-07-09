import { useState } from "react";
import NodeSidebar from "./components/NodeSidebar";
import WorkflowCanvas from "./components/WorkflowCanvas";
import { useWorkflowStore } from "./store/workflowStore";
import { toWorkflowJSON, validateWorkflow, runWorkflow } from "./services/workflowApi";
import "./App.css";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const { nodes, edges } = useWorkflowStore();

  const handleRunWorkflow = async () => {
    try {
      setLoading(true);
      setResult("");

      const workflowJSON = toWorkflowJSON(nodes, edges);

      workflowJSON.prompt = prompt;

      const validation = await validateWorkflow(workflowJSON);

      if (!validation.valid) {
        setResult(`Validation failed: ${validation.errors.join(", ")}`);
        return;
      }

      const response = await runWorkflow(workflowJSON);

      setResult(JSON.stringify(response, null, 2));
    } catch (error) {
      setResult(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <NodeSidebar />

      <main className="main-area">
        <div className="prompt-bar">
          <input
            className="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want the agents to do..."
          />

          <button
            className="run-button"
            onClick={handleRunWorkflow}
            disabled={loading}
          >
            {loading ? "Running..." : "Run Workflow"}
          </button>
        </div>

        {result && <pre className="result-box">{result}</pre>}

        <WorkflowCanvas />
      </main>
    </div>
  );
}