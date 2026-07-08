import { create } from 'zustand';
import { applyNodeChanges, applyEdgeChanges, addEdge } from '@xyflow/react';

export const useWorkflowStore = create((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,

  onNodesChange: (changes) =>
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    }),

  onEdgesChange: (changes) =>
    set({
      edges: applyEdgeChanges(changes, get().edges),
    }),

  onConnect: (params) =>
    set({
      edges: addEdge(
        {
          ...params,
          animated: true,
          markerEnd: {
            type: 'arrowclosed',
            color: '#6ea8fe',
          },
        },
        get().edges
      ),
    }),

  addNode: (node) =>
    set({
      nodes: [...get().nodes, node],
    }),

  setSelectedNode: (id) =>
    set({
      selectedNodeId: id,
    }),

  updateNodeConfig: (id, config) =>
    set({
      nodes: get().nodes.map((node) =>
        node.id === id
          ? {
              ...node,
              data: {
                ...node.data,
                config,
              },
            }
          : node
      ),
    }),
}));