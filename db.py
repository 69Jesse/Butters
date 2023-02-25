import asyncpg


class Database:
    # TODO: make this actually do stuff
    async def __aenter__(self) -> ...:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    def __str__(self) -> str:
        return self.__class__.__name__
