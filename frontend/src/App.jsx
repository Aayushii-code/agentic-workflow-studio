import NodeSidebar from './components/NodeSidebar';
import WorkflowCanvas from './components/WorkflowCanvas';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <NodeSidebar />

      <main className="main-area">
        <div className="prompt-bar">
          <input
            className="prompt-input"
            placeholder="Describe what you want the agents to do..."
          />
          <button className="run-button">Run Workflow</button>
        </div>

        <WorkflowCanvas />
      </main>
    </div>
  );
}