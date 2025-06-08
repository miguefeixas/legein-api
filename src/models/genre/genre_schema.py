from pydantic import BaseModel


class GenreBaseSchema(BaseModel):
    """
    Genre base schema
    """

    id: int
    name: str
