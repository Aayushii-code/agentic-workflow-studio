import { Handle, Position } from '@xyflow/react';

export default function InputNode({ data }) {
  return (
    <div className="input-node">
      <strong>{data.config?.name || 'Input'}</strong>
      <div className="node-status">{data.status || '○ Waiting'}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}