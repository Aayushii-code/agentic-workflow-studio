import { Handle, Position } from '@xyflow/react';

export default function AgentNode({ data }) {
  return (
    <div className="agent-node">
      <Handle type="target" position={Position.Top} />
      <strong>{data.config?.name || 'Agent'}</strong>
      <div className="node-status">{data.status || '○ Waiting'}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}