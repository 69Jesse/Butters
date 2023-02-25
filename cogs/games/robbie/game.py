from .other import (
    STANDARD_LEVEL_LINES,
)

from .level import Level

from typing import (
    Optional,
)


class Game:
    def __init__(self, lines: Optional[list[str]] = None) -> None:
        lines = lines or STANDARD_LEVEL_LINES
        self.levels: list[Level] = [Level.from_line(game=self, line=line) for line in lines]
        self.reset(levels=False)

    @property
    def level(self) -> Level:
        return self.levels[self.level_index]

    @property
    def score(self) -> int:
        return sum(level.score for level in self.levels)

    @property
    def total_moves(self) -> int:
        return sum(level.moves for level in self.levels)

    @property
    def completed(self) -> bool:
        return all(level.completed for level in self.levels)

    def next_level(self, n: int = 1) -> None:
        self.level_index = (self.level_index + n) % len(self.levels)

    def reset(self, levels: bool = True) -> None:
        self.level_index = 0
        if levels:
            for level in self.levels:
                level.reset()
        self.tries_left = 3

    @property
    def started(self) -> Optional[float]:
        try:
            return min(level.started for level in self.levels if level.started is not None)
        except ValueError:
            return None
