import asyncio

from app.database import Base, engine
from app.models import document as _models  # noqa: F401


def pytest_configure(config):
    """Create all database tables before any test runs."""
    asyncio.run(_create_tables())


async def _create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
