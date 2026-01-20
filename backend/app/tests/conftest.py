"""
Pytest configuration and fixtures
"""
import asyncio
import pytest
from tortoise import Tortoise


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.
    This prevents the "Event loop is closed" error.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    """
    Initialize and cleanup for all tests.
    Ensures database connections are properly closed.
    """
    yield
    # Cleanup after all tests
    try:
        await Tortoise.close_connections()
    except Exception:
        pass  # Ignore if already closed
