# Agentic Workflow Studio

## Overview
Agentic Workflow Studio is a low-code platform that allows users to create AI workflows using a drag-and-drop interface. Users can connect nodes, configure them, and execute workflows through a FastAPI backend.

---

## Features
- Drag-and-drop workflow builder
- Visual node connections
- Configurable nodes
- Workflow JSON generation
- FastAPI backend integration
- Workflow validation
- Extensible architecture

---

## Tech Stack

### Frontend
- React
- React Flow
- JavaScript
- CSS

### Backend
- FastAPI
- Python
- Pydantic

---

## Architecture

```
User
  ↓
React Frontend
  ↓
Workflow JSON
  ↓
FastAPI Backend
  ↓
Workflow Engine
  ↓
Node Executors
  ↓
Output
```

---

## Project Structure

```
workflow-studio/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── nodes/
│   └── services/
│
├── backend/
│   ├── app/
│   ├── api/
│   ├── schemas/
│   ├── engine/
│   └── main.py
│
└── README.md
```

---

## Supported Nodes

- Input
- Agent
- Tool
- Output

---

## API Endpoints

| Method | Endpoint |
|---------|----------|
| GET | /health |
| POST | /api/workflows/validate |
| POST | /api/workflows/run |

---

## Run the Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend:
```
http://127.0.0.1:8000
```

Swagger Docs:
```
http://127.0.0.1:8000/docs
```

---

## Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Team

**Aayushi Sora**
- Backend
- Workflow Engine
- FastAPI Integration

**Anushka Prasad**
- Frontend
- Drag-and-Drop UI
- Workflow JSON

**Neha A. Rao**
- Node Executors
- Configuration
- Testing

---

## Future Enhancements

- AI model integration
- Database support
- Workflow templates
- Authentication
- Agent Marketplace integration
