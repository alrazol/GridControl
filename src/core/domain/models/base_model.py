from pydantic import BaseModel


class BaseConfigModel(BaseModel):
    class Config:
        extra = "forbid"
