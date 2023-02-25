from PIL import Image

from .other import (
    AwayPosition,
    Direction,
    Position,
)

from typing import (
    TYPE_CHECKING,
    Optional,
)
if TYPE_CHECKING:
    from .level import Level


BASE_IMAGE_PATH = r'assets/robbie/'

import logging
log = logging.getLogger(__name__)


class Asset:
    id: int
    paths: list[str]
    images: list[Image.Image]
    def __init__(self, level: Optional['Level'] = None, position: Optional[Position] = None) -> None:
        self.level: 'Level' = level  # type: ignore
        self.position: Position = position  # type: ignore
        # .level and .position can be None here when immidiately after creating an asset.
        # For example when using Level.__setitem__ with the creation.
        # Example: `self.level[Position(6, 9)] = Trees()`` instead of `Trees(level=self.level, position=Position(6, 9))``

    def __init_subclass__(cls, id: Optional[int] = None, paths: Optional[list[str]] = None, include_default: bool = True) -> None:
        if id is None: return
        assert 1 <= id <= 99
        cls.id = id
        cls.paths = ([f'{cls.id}.png'] if include_default else []) + ([f'{cls.id}_{path}.png' for path in paths] if paths is not None else [])
        cls.images: list[Image.Image] = []
        for path in cls.paths:
            try:
                cls.images.append(Image.open(f'{BASE_IMAGE_PATH}{path}').convert('RGBA'))
            except FileNotFoundError:
                log.error(f'Image not found: {path}')

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.position})'

    def can_enter(self) -> bool:
        return True

    def on_enter(self) -> None:
        pass

    def after_every_move(self) -> None:
        pass

    def image(self) -> Image.Image:
        return self.images[0]


class Tile(Asset):
    def can_leave(self) -> bool:
        return self.can_enter()  # Should actually reverse the direction, but that's not a problem anywhere so I'm not gonna bother.


class Item(Asset):
    def after_every_move(self) -> None:
        if isinstance(self.level.tile(self.position), Water1):
            self.position = AwayPosition


class Walkable(Tile):
    directions: tuple[Direction, ...]
    def __init_subclass__(cls, directions: Optional[tuple[Direction, ...]] = None, **kwargs) -> None:
        directions = directions or tuple(Direction)
        assert 1 <= len(directions) <= 4 and all(d in Direction for d in directions)
        cls.directions = directions
        return super().__init_subclass__(**kwargs)

    def can_enter(self) -> bool:
        return self.level.robbie.direction in self.directions


class Solid(Tile):
    def can_enter(self) -> bool:
        return False


class Moveable(Item):
    directions: tuple[Direction, ...]
    def __init_subclass__(cls, directions: tuple[Direction, ...], **kwargs) -> None:
        assert 1 <= len(directions) <= 4 and all(d in Direction for d in directions)
        cls.directions = directions
        return super().__init_subclass__(**kwargs)

    def can_move(self, extra: tuple[type[Asset], ...] = ()) -> bool:
        position = self.position + self.level.robbie.direction.value
        tile = self.level.tile(position)  # None if position is out of bounds
        item = self.level.item(position)
        return tile is not None and item is None and isinstance(tile, (
            Empty,
            Water1,
            BridgeHorizontalClosed,
            BridgeVerticalClosed,
        ) + extra)

    def can_enter(self) -> bool:
        return self.level.robbie.direction in self.directions and self.can_move()

    def on_move(self) -> None:
        position = self.position + self.level.robbie.direction.value
        self.position = position

    def on_enter(self) -> None:
        self.on_move()


class Collectable(Item):
    def on_collect(self) -> None:
        self.position = AwayPosition

    def on_enter(self) -> None:
        self.on_collect()


class Empty(Walkable, id=1): pass
class RedHouse(Solid, id=2): pass
class BlueHouse(Solid, id=3): pass
class Windmill(Solid, id=4): pass
class Flowers(Solid, id=5): pass
class Trees(Solid, id=6): pass
class Walls(Solid, id=7): pass
class FenceHorizontalOpen(Walkable, id=8, directions=(Direction.down, Direction.up)): pass
class FenceHorizontalClosed(Solid, id=9): pass
class FenceVerticalOpen(Walkable, id=10, directions=(Direction.right, Direction.left)): pass
class FenceVerticalClosed(Solid, id=11): pass


class Water1(Walkable, id=12):
    def on_enter(self) -> None:
        self.level.failed = True


class Water2(Water1, id=13): pass
class Water3(Water1, id=14): pass
class Water4(Water1, id=15): pass
class Water5(Water1, id=16): pass
class BridgeHorizontalClosed(Walkable, id=17): pass
class BridgeHorizontalOpen(Water1, id=18): pass
class BridgeVerticalClosed(Walkable, id=19): pass
class BridgeVerticalOpen(Water1, id=20): pass
class Leaves(Walkable, id=21, paths=['right', 'down', 'left', 'up']):
    def on_enter(self) -> None:
        self.level.failed = True

    def image(self) -> Image.Image:
        return self.images[0] if self.level.robbie.position != self.position else self.images[int(self.level.robbie.direction) + 1]


class RedButtonOn(Walkable, id=22):
    def toggle(self) -> None:
        for tile in self.level.tiles.values():
            if isinstance(tile, (FenceHorizontalOpen, FenceHorizontalClosed, FenceVerticalOpen, FenceVerticalClosed)):
                self.level[tile.position] = {
                    FenceHorizontalOpen: FenceHorizontalClosed,
                    FenceHorizontalClosed: FenceHorizontalOpen,
                    FenceVerticalOpen: FenceVerticalClosed,
                    FenceVerticalClosed: FenceVerticalOpen,
                }[type(tile)]()

    def on_enter(self) -> None:
        self.toggle()
        self.level[self.position] = RedButtonOff()


class RedButtonOff(RedButtonOn, id=23):
    def on_enter(self) -> None:
        self.toggle()
        self.level[self.position] = RedButtonOn()


class BlueButtonOn(Walkable, id=24):
    def toggle(self) -> None:
        for tile in self.level.tiles.values():
            if isinstance(tile, (BridgeHorizontalClosed, BridgeHorizontalOpen, BridgeVerticalClosed, BridgeVerticalOpen)):
                self.level[tile.position] = {
                    BridgeHorizontalClosed: BridgeHorizontalOpen,
                    BridgeHorizontalOpen: BridgeHorizontalClosed,
                    BridgeVerticalClosed: BridgeVerticalOpen,
                    BridgeVerticalOpen: BridgeVerticalClosed,
                }[type(tile)]()

    def on_enter(self) -> None:
        self.toggle()
        self.level[self.position] = BlueButtonOff()


class BlueButtonOff(BlueButtonOn, id=25):
    def on_enter(self) -> None:
        self.toggle()
        self.level[self.position] = BlueButtonOn()


class DogHouseDown(Solid, id=26, paths=['inside']):
    def can_enter(self) -> bool:
        return self.level.robbie.direction == Direction.up

    def on_enter(self) -> None:
        self.level.completed = True

    def image(self) -> Image.Image:
        return self.images[self.level.robbie.position == self.position]


class DogHouseRight(DogHouseDown, id=27, paths=['inside']):
    def can_enter(self) -> bool:
        return self.level.robbie.direction == Direction.left


class Bone(Collectable, id=28):
    def on_enter(self) -> None:
        self.level.score += 10
        return super().on_enter()


class Potion(Collectable, id=29):
    def on_enter(self) -> None:
        self.level.game.tries_left += 1
        return super().on_enter()


class DogCage(Solid, id=30): pass
class CatCage(Solid, id=31): pass


class Dog(Solid, id=32, paths=['right', 'down', 'left', 'up', 'fighting']):
    def looking_direction(self) -> Direction:
        single = (self.level.robbie.position - self.position).single()
        return Direction({
            Position(-1, -1): Direction.left,
            Position(-1, 1): Direction.down,
            Position(1, -1): Direction.up,
            Position(1, 1): Direction.right,
        }.get(single, single))

    def should_attack(self, alert: bool = False) -> bool:
        for xy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            position = self.position + xy
            while True:
                if position == self.level.robbie.position:
                    return True
                elif not (alert or (isinstance(self.level.tile(position), Empty) and self.level.item(position) is None)) or not self.level.in_bounds(position):
                    break
                position += xy
        return False

    def after_every_move(self) -> None:
        if self.should_attack():
            self.level[self.position] = Empty()
            self.level[self.level.robbie.position] = self.__class__()
            self.level.failed = True

    def image(self) -> Image.Image:
        return self.images[
            5 if self.level.robbie.position == self.position else
            (int(self.looking_direction()) + 1)
            if self.should_attack(alert=True) else 0
        ]


class Cat(Dog, id=37, paths=['right', 'down', 'left', 'up', 'fighting']):
    def should_attack(self, alert: bool = False) -> bool:
        return self.level.robbie.position.distance(self.position) <= 1 + alert


class Ball(Moveable, id=51, directions=tuple(Direction)): pass
class CartVertical(Moveable, id=52, directions=(Direction.up, Direction.down)): pass
class CartHorizontal(Moveable, id=53, directions=(Direction.left, Direction.right)): pass
class Shoe(Moveable, id=54, directions=tuple(Direction)): pass


class Chainsaw(Moveable, id=55, directions=tuple(Direction)):
    def can_move(self) -> bool:
        return super().can_move(extra=(Trees,))

    def on_move(self) -> None:
        super().on_move()
        tile = self.level.tile(self.position)
        if isinstance(tile, Trees):
            self.level[self.position] = Empty()


class Cage(Moveable, id=57, directions=tuple(Direction)):
    def can_move(self) -> bool:
        return super().can_move(extra=(Dog, Cat))

    def on_move(self) -> None:
        super().on_move()
        tile = self.level.tile(self.position)
        if isinstance(tile, (Dog, Cat)):
            self.level[self.position] = {
                True: DogCage,
                False: CatCage,
            }[type(tile) == Dog]()
            self.position = AwayPosition


class RobbieAsset(Asset, id=80, paths=['right', 'down', 'left', 'up', 'drowning'], include_default=False):
    def image(self, position: Position) -> Optional[Image.Image]:
        """Returns None if the asset is not to be drawn."""
        tile = self.level.tile(position)
        if isinstance(tile, (
            Leaves, Dog, Cat, DogHouseDown, DogHouseRight,
        )):
            return None
        elif isinstance(tile, Water1):
            return self.images[4]
        else:
            return self.images[int(self.level.robbie.direction)]


ID_TO_ASSET: dict[int, type[Asset]] = {
    variable.id: variable
    for variable in list(globals().values())
    if isinstance(variable, type)
    and issubclass(variable, Asset)
    and hasattr(variable, 'id')
}
ALL_ASSET_IDS: list[int] = list(ID_TO_ASSET.keys())
