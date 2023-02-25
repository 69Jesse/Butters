import asyncio
from bot import Butters
from config import TOKEN

import sys
import os
from pathlib import Path

import logging
from logger import SetupLogging


async def run() -> None:
    log = logging.getLogger()
    log.info(f'{Path().absolute()} {sys.executable.split(os.sep)[-1]} {" ".join(sys.argv)}')
    log.info(r'Source at https://github.com/69Jesse/Butters')

    bot = Butters()
    await bot.start(TOKEN)


def main() -> None:
    with SetupLogging():
        asyncio.run(run())


if __name__ == '__main__':
    main()


import difflib
words = ['hello', 'hi', 'hey', 'howdy', 'hey there']
difflib.get_close_matches('h', words)
import keyword
keyword.kwlist