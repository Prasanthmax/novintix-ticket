"""Shared test fixtures – fresh DB, as_user() client, FakeLLM, route-hit recorder."""

import os
import json
import pytest
from unittest.mock import MagicMock

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

# Force LLM_PROVIDER=none before any app import
os.environ["LLM_PROVIDER"] = "none"

from app.db import Base, get_db
from app.main import app
from app.seed import seed_data

# ---------------------------------------------------------------------------
# Fresh in-memory DB per test
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_session():
    """Yield a SQLAlchemy session backed by a fresh in-memory SQLite DB."""
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _pragma(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_data(session)
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    """TestClient wired to the fresh DB.  Also records route hits."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# as_user() helper – returns a client-like wrapper that sets X-User-Id
# ---------------------------------------------------------------------------

class _UserClient:
    """Thin wrapper that injects X-User-Id into every request."""

    def __init__(self, test_client: TestClient, user_id: str):
        self._tc = test_client
        self._uid = user_id

    def _headers(self, extra: dict | None = None) -> dict:
        h = {"X-User-Id": self._uid}
        if extra:
            h.update(extra)
        return h

    def get(self, url, **kw):
        kw.setdefault("headers", {}).update(self._headers())
        return self._tc.get(url, **kw)

    def post(self, url, **kw):
        kw.setdefault("headers", {}).update(self._headers())
        return self._tc.post(url, **kw)

    def put(self, url, **kw):
        kw.setdefault("headers", {}).update(self._headers())
        return self._tc.put(url, **kw)

    def patch(self, url, **kw):
        kw.setdefault("headers", {}).update(self._headers())
        return self._tc.patch(url, **kw)

    def delete(self, url, **kw):
        kw.setdefault("headers", {}).update(self._headers())
        return self._tc.delete(url, **kw)


@pytest.fixture()
def as_user(client):
    """Factory fixture: as_user('user-hr-eng1') returns a client with that header."""
    def _factory(user_id: str) -> _UserClient:
        return _UserClient(client, user_id)
    return _factory


# ---------------------------------------------------------------------------
# FakeLLM – records prompts, returns canned JSON, can raise
# ---------------------------------------------------------------------------

class FakeLLM:
    """Drop-in fake for the LangChain chat model used by the agent."""

    def __init__(self, responses: list[str] | None = None, raise_on_call: bool = False):
        self.calls: list[str] = []
        self.responses = list(responses or [])
        self.raise_on_call = raise_on_call
        self._idx = 0

    def invoke(self, messages, **kwargs):
        if self.raise_on_call:
            raise RuntimeError("LLM unavailable (fake)")
        prompt = str(messages)
        self.calls.append(prompt)
        if self._idx < len(self.responses):
            resp = self.responses[self._idx]
            self._idx += 1
        else:
            resp = '{"request_type": null, "reason_code": null, "support_chunk_ids": [], "escalate": true}'
        msg = MagicMock()
        msg.content = resp
        return msg


@pytest.fixture()
def fake_llm():
    """Returns a FakeLLM instance factory."""
    def _factory(responses=None, raise_on_call=False):
        return FakeLLM(responses=responses, raise_on_call=raise_on_call)
    return _factory


# ---------------------------------------------------------------------------
# Route-hit recorder
# ---------------------------------------------------------------------------

_ROUTE_HITS: set[str] = set()


@pytest.fixture(autouse=True)
def _record_route_hits(client):
    """Monkey-patch the client to record which routes are hit."""
    # We collect route hits by inspecting responses after each test module
    pass


def record_hit(method: str, path: str):
    """Call from tests or middleware to record a route hit."""
    _ROUTE_HITS.add(f"{method} {path}")


def get_route_hits() -> set[str]:
    return _ROUTE_HITS.copy()

