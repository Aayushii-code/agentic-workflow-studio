import { Handle, Position } from '@xyflow/react';

export default function ToolNode({ data }) {
  return (
    <div className="tool-node">
      <Handle type="target" position={Position.Top} />
      <strong>{data.config?.name || 'Tool'}</strong>
      <div className="node-status">{data.status || 'Waiting'}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}