"""Test helpers for importing and exercising app.py without a real Streamlit runtime."""

from __future__ import annotations

import importlib
import sys
import types
from unittest.mock import patch


class SessionState(dict):
    """Dict-like session state with attribute access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class DummyContext:
    """Simple context manager used for columns/expanders."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyProgress:
    """Tracks progress updates."""

    def __init__(self, start_value: int):
        self.values = [start_value]
        self.cleared = False

    def progress(self, value: int):
        self.values.append(value)

    def empty(self):
        self.cleared = True


class DummyStatus:
    """Tracks markdown status updates."""

    def __init__(self):
        self.messages = []
        self.cleared = False

    def markdown(self, value: str):
        self.messages.append(value)

    def empty(self):
        self.cleared = True


class UploadedFileStub:
    """Simple uploaded file object compatible with st.file_uploader output."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


class StreamlitStub(types.ModuleType):
    """Small streamlit shim to execute app code in tests."""

    def __init__(self):
        super().__init__("streamlit")
        self.session_state = SessionState()
        self.page_config = {}
        self.markdown_calls = []
        self.dataframe_calls = []
        self.download_calls = []
        self.progress_objects = []
        self.status_objects = []
        self.file_uploader_return = None
        self.selectbox_returns = {}
        self.checkbox_returns = {}
        self.multiselect_return = None
        self.button_returns = {}
        self.rerun_called = False

    def cache_data(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def set_page_config(self, **kwargs):
        self.page_config = kwargs

    def markdown(self, *args, **kwargs):
        self.markdown_calls.append((args, kwargs))

    def columns(self, spec):
        count = spec if isinstance(spec, int) else len(spec)
        return [DummyContext() for _ in range(count)]

    def expander(self, *args, **kwargs):
        return DummyContext()

    def file_uploader(self, *args, **kwargs):
        return self.file_uploader_return

    def selectbox(self, label, options, index=0, key=None, **kwargs):
        identifier = key or label
        if identifier in self.selectbox_returns:
            return self.selectbox_returns[identifier]
        if options:
            return options[index]
        return None

    def button(self, label, key=None, **kwargs):
        identifier = key or label
        value = self.button_returns.get(identifier, self.button_returns.get(label, False))
        if isinstance(value, list):
            return value.pop(0) if value else False
        return value

    def checkbox(self, label, value=False, key=None, **kwargs):
        identifier = key or label
        return self.checkbox_returns.get(identifier, value)

    def multiselect(self, label, options, default=None, key=None, **kwargs):
        if self.multiselect_return is not None:
            return self.multiselect_return
        return default

    def dataframe(self, *args, **kwargs):
        self.dataframe_calls.append((args, kwargs))

    def progress(self, value):
        progress = DummyProgress(value)
        self.progress_objects.append(progress)
        return progress

    def empty(self):
        status = DummyStatus()
        self.status_objects.append(status)
        return status

    def download_button(self, *args, **kwargs):
        self.download_calls.append((args, kwargs))

    def rerun(self):
        self.rerun_called = True


def import_app_with_stub(stub: StreamlitStub | None = None):
    """Import app.py with a Streamlit stub injected into sys.modules."""
    streamlit_stub = stub or StreamlitStub()
    sys.modules.pop("app", None)

    with patch.dict(sys.modules, {"streamlit": streamlit_stub}):
        import app  # pylint: disable=import-error

        app_module = importlib.reload(app)

    return app_module, streamlit_stub
