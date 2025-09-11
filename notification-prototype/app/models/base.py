from pydantic import BaseModel, Field

class SimulatePayload(BaseModel):
    n_orders: int = Field(gt=0, le=5000)
    min_delay_ms: int = Field(default=300, ge=0)
    max_delay_ms: int = Field(default=1200, ge=0)
