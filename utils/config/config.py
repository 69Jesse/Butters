"""Mostly stolen from Danny"""
import json
import os
import asyncio

from typing import (
    Callable,
    Optional,
    Generic,
    TypeVar,
    Any,
)


__all__ = (
    'Config',
)

_T = TypeVar('_T')

ObjectHook = Callable[[dict[str, Any]], Any]

path = __name__.replace('.', os.sep) + os.sep + 'files' + os.sep


class Config(Generic[_T]):
    def __init__(self, name: str, object_hook: Optional[ObjectHook] = None, encoder: Optional[type[json.JSONEncoder]] = None, load_later: bool = False) -> None:
        self.name = name
        self.path = path + name
        self.object_hook = object_hook
        self.encoder = encoder
        self.loop = asyncio.get_running_loop()
        self.lock = asyncio.Lock()
        self._db: dict[str, _T | Any] = {}
        if load_later:
            self.loop.create_task(self.load())
        else:
            self.load_from_file()

    def load_from_file(self) -> None:
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self._db = json.load(f, object_hook=self.object_hook)
        except FileNotFoundError:
            self._db = {}

    async def load(self) -> None:
        async with self.lock:
            await self.loop.run_in_executor(None, self.load_from_file)

    def _dump(self) -> None:
        temp = path + f'{os.urandom(16).hex()}-{self.name}.tmp'
        with open(temp, 'w', encoding='utf-8') as tmp:
            json.dump(self._db.copy(), tmp, ensure_ascii=True, cls=self.encoder, separators=(',', ':'))

        # atomically move the file
        os.replace(temp, self.path)

    async def save(self) -> None:
        async with self.lock:
            await self.loop.run_in_executor(None, self._dump)

    def get(self, key: Any, default: Any = None) -> Optional[_T | Any]:
        """Retrieves a config entry."""
        return self._db.get(str(key), default)

    async def put(self, key: Any, value: _T | Any) -> None:
        """Edits a config entry."""
        self._db[str(key)] = value
        await self.save()

    async def remove(self, key: Any) -> None:
        """Removes a config entry."""
        del self._db[str(key)]
        await self.save()

    def __contains__(self, item: Any) -> bool:
        return str(item) in self._db

    def __getitem__(self, item: Any) -> _T | Any:
        return self._db[str(item)]

    def __len__(self) -> int:
        return len(self._db)

    def all(self) -> dict[str, _T | Any]:
        return self._db

    def __str__(self) -> str:
        return str(self.all())
