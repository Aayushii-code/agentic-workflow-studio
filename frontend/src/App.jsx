import NodeSidebar from './components/NodeSidebar';
import WorkflowCanvas from './components/WorkflowCanvas';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <NodeSidebar />
      <WorkflowCanvas />
    </div>
  );
}