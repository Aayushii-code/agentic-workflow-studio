from fastapi import FastAPI

from app.api.workflow import router as workflow_router


app = FastAPI(
    title="Agentic Workflow Studio API",
    version="0.1.0",
)

app.include_router(workflow_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    } 