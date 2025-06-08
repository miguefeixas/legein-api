from typing import Optional

from pydantic import BaseModel


class AuthorBaseSchema(BaseModel):
    """
    Author base schema
    """

    id: int
    name: str
    first_last_name: str
    second_last_name: Optional[str]
    full_name: str
