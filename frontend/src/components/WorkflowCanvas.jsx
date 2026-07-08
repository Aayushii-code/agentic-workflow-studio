import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
  useReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useEffect } from 'react';
import { useWorkflowStore } from '../store/workflowStore';
import InputNode from '../nodes/InputNode';
import AgentNode from '../nodes/AgentNode';
import ToolNode from '../nodes/ToolNode';
import OutputNode from '../nodes/OutputNode';

const nodeTypes = {
  input: InputNode,
  agent: AgentNode,
  tool: ToolNode,
  output: OutputNode,
};

function CanvasInner() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    setSelectedNode,
  } = useWorkflowStore();

  const { screenToFlowPosition, fitView } = useReactFlow();

  useEffect(() => {
  fitView({
    padding: 0.2,
    duration: 400,
  });
}, [nodes.length, fitView]);

  const onDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const onDrop = (event) => {
    event.preventDefault();

    const type = event.dataTransfer.getData('application/reactflow');
    if (!type) return;

    const position = screenToFlowPosition({
      x: event.clientX,
      y: event.clientY,
    });

    addNode({
      id: `${type}-${Date.now()}`,
      type,
      position,
      data: {
        label: type.charAt(0).toUpperCase() + type.slice(1),
        config: {},
        status: '○ Waiting',
      },
    });
  };

  return (
    <div className="canvas-wrapper" onDrop={onDrop} onDragOver={onDragOver}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_, node) => setSelectedNode(node.id)}
        snapToGrid
        snapGrid={[20, 20]}
        defaultEdgeOptions={{
          markerEnd: {
            type: 'arrowclosed',
            color: '#6ea8fe',
          },
        }}
        fitView
      >
        <Background color="#2a2e3a" gap={20} />

        <Controls />

        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'input') return '#f2a93b';
            if (node.type === 'agent') return '#6ea8fe';
            if (node.type === 'tool') return '#4fd88a';
            if (node.type === 'output') return '#b8c0cc';
            return '#8b93a3';
          }}
          maskColor="rgba(15, 17, 23, 0.75)"
          pannable
          zoomable
        />
      </ReactFlow>
    </div>
  );
}

export default function WorkflowCanvas() {
  return (
    <ReactFlowProvider>
      <CanvasInner />
    </ReactFlowProvider>
  );
}