from typing import (
    Iterator,
    Iterable,
    Optional,
    Callable,
    Any,
)
from typing_extensions import (
    Self,
)


__all__ = (
    'Point',
    '_Position',
)


class Point:
    def __init__(self, x: int, y: int) -> None:
        assert all(isinstance(v, int) for v in (x, y)), f'Expected int, got `{x.__class__.__name__}` and `{y.__class__.__name__}`'
        self.x = x
        self.y = y

    def __iter__(self) -> Iterator[int]:
        return iter((self.x, self.y))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'({self.x},{self.y})'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, (tuple, list)):
            return self.x == other[0] and self.y == other[1]
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(tuple(self))

    def _addsub(self, other: Any, n: int) -> Self:
        if isinstance(other, Point):
            return self.__class__(self.x + other.x * n, self.y + other.y * n)
        elif isinstance(other, (tuple, list)):
            x: int = self.x + other[0] * n
            y: int = self.y + other[1] * n
            return self.__class__(x, y)
        return NotImplemented

    def __add__(self, other: Any) -> Self:
        return self._addsub(other, 1)

    def __sub__(self, other: Any) -> Self:
        return self._addsub(other, -1)

    def __mul__(self, other: int) -> Self:
        assert isinstance(other, int), f'Expected int, got `{other.__class__.__name__}`'
        return self._addsub(self, other - 1)

    def distance(self, to: Self) -> int:
        return abs(self.x - to.x) + abs(self.y - to.y)


class _Position(Point):
    modulo: Optional[int | tuple[int, int]]
    def __init_subclass__(cls, modulo: Optional[int | tuple[int, int]]) -> None:
        assert (len(modulo) == 2 and all(isinstance(v, int) for v in modulo)) if isinstance(modulo, tuple) else isinstance(modulo, (int, type(None))), f'Expected int, tuple[int, int] or None, got {type(modulo)}'
        cls.modulo = modulo

    def __init__(self, x: int, y: int, *, check_bounds: bool = True) -> None:
        super().__init__(x, y)
        self.in_bounds: bool = True
        if check_bounds:
            self.check_modulo()
        self.checked_bounds: bool = check_bounds

    def check_modulo(self) -> None:
        if self.modulo is None:
            return
        if isinstance(self.modulo, int):
            mx, my = self.modulo, self.modulo
            if not all(0 <= v < self.modulo for v in (self.x, self.y)):
                self.in_bounds = False
        elif isinstance(self.modulo, tuple):
            mx, my = self.modulo
            if not all(0 <= v < m for v, m in zip((self.x, self.y), self.modulo)):
                self.in_bounds = False
        else:
            raise  # unreachable
        self.x %= mx
        self.y %= my

    @classmethod
    @property
    def up(cls) -> Self:
        return cls(0, -1, check_bounds=False)

    @classmethod
    @property
    def down(cls) -> Self:
        return cls(0, 1, check_bounds=False)

    @classmethod
    @property
    def left(cls) -> Self:
        return cls(-1, 0, check_bounds=False)

    @classmethod
    @property
    def right(cls) -> Self:
        return cls(1, 0, check_bounds=False)

    def flip(self) -> Self:
        return self.__class__(self.y, self.x, check_bounds=self.checked_bounds)

    def move(self, possible: list[Self], direction: Self) -> Self:
        """Move in a direction with possible positions, returns the new position."""
        assert self in possible, f'Expected current position (self) to be in possible positions'
        if len(possible) == 1:
            return self

        """`side` Whether or not the position is on the same side as the moving direction
        C = current position, x = func(p) == True
        Direction Up:
            xxx
            .C.
            ...
        Direction Right:
            ..x
            .Cx
            ..x
        """
        side: Callable[[Self], bool]

        """`line` Whether or not the position is on the same line as the moving direction
        Direction Up & Down:
            .x.
            .C.
            .x.
        Direction Left & Right:
            ...
            xCx
            ...
        """
        line: Callable[[Self], bool]

        try:
            side, line = {
                self.up: (lambda p: p.y < self.y, lambda p: p.x == self.x),
                self.down: (lambda p: p.y > self.y, lambda p: p.x == self.x),
                self.left: (lambda p: p.x < self.x, lambda p: p.y == self.y),
                self.right: (lambda p: p.x > self.x, lambda p: p.y == self.y),
            }[direction]
        except KeyError:
            raise ValueError(f'Expected one of {self.up}, {self.down}, {self.left}, {self.right}, got `{direction}`')

        desired_side: Iterable[Self] = filter(side, possible)
        try:
            """If there is a position on the same line as the current
            position, this returns the closest one to the current position.
            Otherwise this returns the closest possible position in any line.
            Raises ValueError if there is no position on the desired side."""
            return min(desired_side, key=lambda p: (not line(p), self.distance(p)))
        except ValueError:
            """If this is reached, there is no position on the desired side.
            If there is a position on the same line as the current
            position, this returns the furthest one from the current position."""
            return max(filter((lambda p: p not in desired_side and line(p)), possible), key=lambda p: self.distance(p))

    def single(self) -> Self:
        s = lambda v: min(1, max(-1, v))
        return self.__class__(s(self.x), s(self.y), check_bounds=False)
