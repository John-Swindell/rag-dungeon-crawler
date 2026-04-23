import asyncio

from pymongo.errors import PyMongoError

from api.game import engine
from api.state import context, manager


class FailingSessionsCollection:
    async def replace_one(self, *args, **kwargs):
        raise PyMongoError("save failed")

    async def find_one(self, *args, **kwargs):
        raise PyMongoError("load failed")


class FailingContextCollection:
    async def insert_one(self, *args, **kwargs):
        raise PyMongoError("context save failed")


class FailingDB:
    sessions = FailingSessionsCollection()
    context = FailingContextCollection()


def test_manager_save_falls_back_to_memory(monkeypatch):
    manager._sessions.clear()
    state = engine.new_game("Sal")
    disabled = []

    monkeypatch.setattr(manager, "get_db", lambda: FailingDB())
    monkeypatch.setattr(manager, "disable_db", lambda: disabled.append(True))

    asyncio.run(manager.save(state))

    assert manager._sessions[state.session_id] == state
    assert disabled == [True]


def test_manager_load_falls_back_to_memory(monkeypatch):
    manager._sessions.clear()
    state = engine.new_game("Weasel")
    manager._sessions[state.session_id] = state
    disabled = []

    monkeypatch.setattr(manager, "get_db", lambda: FailingDB())
    monkeypatch.setattr(manager, "disable_db", lambda: disabled.append(True))

    loaded = asyncio.run(manager.load(state.session_id))

    assert loaded == state
    assert disabled == [True]


def test_context_save_context_ignores_mongo_errors(monkeypatch):
    state = engine.new_game("Billy")
    disabled = []

    monkeypatch.setattr(context, "get_db", lambda: FailingDB())
    monkeypatch.setattr(context, "disable_db", lambda: disabled.append(True))

    asyncio.run(context.save_context(state, "new_game", "message", "snapshot"))

    assert disabled == [True]
