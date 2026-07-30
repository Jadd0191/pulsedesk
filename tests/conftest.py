"""
Configuración de pytest para pruebas asíncronas.
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para pruebas."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()