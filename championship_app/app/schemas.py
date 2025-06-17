from pydantic import BaseModel

class DriverCreate(BaseModel):
    name: str