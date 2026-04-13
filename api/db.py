from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from api.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_db() -> AsyncIOMotorDatabase:
    return _db


def connect() -> None:
    global _client, _db
    if not settings.mongo_uri:
        return
    _client = AsyncIOMotorClient(settings.mongo_uri)
    _db = _client[settings.mongo_db]


def disconnect() -> None:
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None
