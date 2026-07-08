import { Handle, Position } from '@xyflow/react';

export default function OutputNode({ data }) {
  return (
    <div className="output-node">
      <Handle type="target" position={Position.Top} />
      <strong>{data.config?.name || 'Output'}</strong>
      <div className="node-status">{data.status || 'Waiting'}</div>
    </div>
  );
}