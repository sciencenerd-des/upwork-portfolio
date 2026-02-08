import asyncio
import inspect
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: run async tests with a local asyncio fallback"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    if "asyncio" in pyfuncitem.keywords and inspect.iscoroutinefunction(pyfuncitem.obj):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(pyfuncitem.obj(**pyfuncitem.funcargs))
        finally:
            loop.close()
            asyncio.set_event_loop(None)
        return True
    return None
