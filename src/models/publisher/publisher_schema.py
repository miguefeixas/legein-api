from pydantic import BaseModel


class PublisherBaseSchema(BaseModel):
    """
    Publisher base schema
    """

    id: int
    name: str
