from pydantic import BaseModel


class SubscribeRequest(BaseModel):
    url: str
