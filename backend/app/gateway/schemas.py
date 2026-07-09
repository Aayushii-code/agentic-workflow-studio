from pydantic import BaseModel


class GatewayResponse(BaseModel):
    text: str
    model_used: str
    provider: str
    used_fallback: bool = False
