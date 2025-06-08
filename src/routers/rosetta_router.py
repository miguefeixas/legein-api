from fastapi import APIRouter

from db import SessionLocal

"""
### rosetta_router.py ###

This file contains helper functions for creating routers and database sessions.
"""


def create_router(name: str) -> APIRouter:
    """
    Create a router with the given name
    :param name: The name of the router
    :return: The created router
    """
    return APIRouter(
        prefix='/' + name,
        tags=[name],
    )


def get_db() -> any:
    """
    Get a database session
    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
