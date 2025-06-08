from pydantic import BaseModel


class AccessTokenSchema(BaseModel):
    access_token: str
