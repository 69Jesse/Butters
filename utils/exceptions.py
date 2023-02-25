import traceback as tb
from typing import (
    Collection,
    Optional,
    Callable,
    TypeVar,
)


__all__ = (
    'ValueNotAllowed',
    'valid',
    'traceback',
)


_B = TypeVar('_B')
_A = TypeVar('_A')


class ValueNotAllowed(Exception):
    def __init__(self, cls: Callable[[_B], _A], value: _B, contains: Optional[Collection[_A]] = None, name: Optional[str] = None) -> None:
        base = f'Value **{value}** is not allowed'
        if name is not None:
            base += f' as **{name}**'
        base += f'.\nIt must be of type `{cls.__name__}`'
        if contains is not None:
            seq = f'({", ".join(map(str, contains))})' if not isinstance(contains, range) else (f'{contains.start}-{contains.stop-1}' + f', step {contains.step}'*(contains.step != 1))
            base += f' and inside of `{seq}`'
        base += '.'
        super().__init__(base)


def valid(cls: Callable[[_B], _A], value: _B, *, contains: Optional[Collection[_A]] = None, name: Optional[str] = None) -> _A:
    try:
        if cls == bool and isinstance(value, str):
            value = int(value)
        v = cls(value)
        assert contains is None or v in contains
    except Exception:
        raise ValueNotAllowed(cls=cls, value=value, contains=contains, name=name)
    return v


def traceback(exc: Exception, *, snippet: bool = False) -> str:
    lines: list[str] = []
    for line in tb.format_exception(exc):
        if 'The above exception was the direct cause of the following exception:' in line:
            break
        lines.append(line)
    return '```py\n'*snippet + '\n'.join(lines) + '```'*snippet
