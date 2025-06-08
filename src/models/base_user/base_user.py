from datetime import datetime
from typing import Optional

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.rosetta_item import RosettaItem


class BaseUser(RosettaItem):
    """
    User base class
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    password: Mapped[str] = mapped_column(String(120))
    login_count: Mapped[Optional[int]] = mapped_column(server_default=text('0'))
    logged_at: Mapped[Optional[datetime]]
