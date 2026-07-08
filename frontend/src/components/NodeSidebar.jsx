import { FileInput, Bot, Wrench, FileOutput } from 'lucide-react';

const NODE_GROUPS = [
  { label: 'INPUT', type: 'input', icon: FileInput },
  { label: 'AI AGENTS', type: 'agent', icon: Bot },
  { label: 'TOOLS', type: 'tool', icon: Wrench },
  { label: 'OUTPUT', type: 'output', icon: FileOutput },
];

export default function NodeSidebar() {
  const onDragStart = (event, type) => {
    event.dataTransfer.setData('application/reactflow', type);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="sidebar">
      <h3 className="sidebar-title">Node Palette</h3>

      {NODE_GROUPS.map(({ label, type, icon: Icon }) => (
        <div
          key={type}
          className={`palette-item palette-${type}`}
          draggable
          onDragStart={(event) => onDragStart(event, type)}
        >
          <Icon size={16} />
          <span>{label}</span>
        </div>
      ))}
    </aside>
  );
}