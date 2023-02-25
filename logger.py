"""Mostly stolen from Danny"""
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

import sys
from datetime import datetime

from typing import (
    Any,
)
from typing_extensions import (
    Self,
)


class ColourFormatter(logging.Formatter):
    level_colors: list[tuple[int, str]] = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    formats: dict[int, logging.Formatter] = {
        level: logging.Formatter(
            fmt=f'\x1b[0;1m[\x1b[30;1m%(asctime)s\x1b[0;1m] [\x1b[0m{colour}%(levelname)-7s\x1b[0;1m]\x1b[0m \x1b[35m%(name)s:\x1b[0m %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        for level, colour in level_colors
    }

    def format(self, record: logging.LogRecord) -> str:
        formatter = self.formats.get(record.levelno)
        if formatter is None:
            formatter = self.formats[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output: str = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


class SetupLogging:
    def __init__(
        self,
        stream: bool = True,
        max_bytes: int = 32*1024*1024,
        backup_count: int = 5,
        date_format: str = '%Y-%m-%d %H:%M:%S',
    ) -> None:
        self.log = logging.getLogger()
        self.stream = stream
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.date_format = date_format

    def __enter__(self) -> Self:
        self.log.setLevel(logging.INFO)

        handlers: list[tuple[logging.Handler, logging.Formatter]] = [(
            RotatingFileHandler(
                filename=f'logs/{datetime.now().strftime(self.date_format.replace(":", "-"))}.log',
                encoding='utf-8',
                mode='w',
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
            ),
            logging.Formatter(
                fmt='[{asctime}] [{levelname:<7}] {name}: {message}',
                datefmt=self.date_format,
                style='{',
            ),
        )]
        if self.stream:
            handlers.append((
                StreamHandler(sys.stdout),
                ColourFormatter(),
            ))

        for handler, formatter in handlers:
            handler.setFormatter(formatter)
            self.log.addHandler(handler)

        return self

    def __exit__(self, *args: Any) -> None:
        handlers = self.log.handlers[:]
        for handler in handlers:
            handler.close()
            self.log.removeHandler(handler)
