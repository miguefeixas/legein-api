from src.routers.rosetta_router import create_router

api_name = 'health'

router = create_router(api_name)


@router.get('/')
async def read_health() -> dict[str, str]:
    """
    Health check endpoint
    """
    return {'status': 'ok'}
