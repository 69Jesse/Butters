from PIL import Image
import re

from .other import (
    Position,
    Direction,
)
from .assets import (
    ALL_ASSET_IDS,
    DogHouseRight,
    DogHouseDown,
    ID_TO_ASSET,
    RobbieAsset,
    Walkable,
    Solid,
    Asset,
    Empty,
    Tile,
    Item,
)

import time

from typing import (
    TYPE_CHECKING,
    Optional,
)
from typing_extensions import (
    Self,
)
if TYPE_CHECKING:
    from .game import Game


THOMAS: Image.Image = Image.open('assets/robbie/thomas.png').convert('RGBA')
TILE_SIZE: tuple[int, int] = (48, 36)
TILE_OFFSET: tuple[int, int] = (6, 82)


class Robbie:
    def __init__(self, level: 'Level', asset: RobbieAsset) -> None:
        self.level = level
        self.asset = asset
        self.position = self.asset.position
        del self.asset.position
        self.direction = Direction.right


class Level:
    line: str
    def __init__(self, game: 'Game', assets: list[Asset]) -> None:
        self.game = game
        self.assets = assets
        for asset in self.assets:
            asset.level = self
        self.dimensions: tuple[int, int] = (max(asset.position.x for asset in self.assets) + 1, max(asset.position.y for asset in self.assets) + 1)
        if not all(len([asset for asset in self.assets if asset.position.y == y]) == self.dimensions[0] for y in range(self.dimensions[1])):
            raise ValueError('Level is not rectangular.')
        elif not all(3 <= d <= 25 for d in self.dimensions):
            raise ValueError('Level is too big/small.')
        elif sum(isinstance(asset, RobbieAsset) for asset in self.assets) != 1:
            raise ValueError('There must be exactly one Robbie. (id 80)')
        elif sum(isinstance(asset, (DogHouseDown, DogHouseRight)) for asset in self.assets) < 1:
            raise ValueError('There must be at least one dog house. (id 26/27)')
        self.set_line()
        self.tiles: dict[Position, Tile] = {
            asset.position: asset
            for asset in self.assets
            if isinstance(asset, Tile)
        }
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                if Position(x, y) not in self.tiles:
                    self[Position(x, y)] = Empty()
        self.items: list[Item] = [
            asset for asset in self.assets
            if isinstance(asset, Item)
        ]
        self.robbie = Robbie(level=self, asset=next(asset for asset in self.assets if isinstance(asset, RobbieAsset)))
        self.failed: bool = False
        self.completed: bool = False
        self.score: int = 0
        self.moves: int = 0
        self.started: Optional[float] = None

    @classmethod
    def from_line(cls, game: 'Game', line: str) -> Self:
        """Raises ValueError if the line is invalid."""
        if not isinstance(line, str):
            raise ValueError('Invalid line.')
        if len(line) == 216 and '-' not in line:
            line = '-'.join(line[i:i+24] for i in range(0, len(line), 24))
        match = re.match(r'([0-9]{2}-?)+', line)
        if not match:
            raise ValueError('Invalid line.')
        assets: list[Asset] = []
        rows = line.split('-')
        if not all(len(row) % 2 == 0 for row in rows):
            raise ValueError('Invalid line.')
        if not all(len(row) == len(rows[0]) for row in rows):
            raise ValueError('Level is not rectangular.')
        for y, row in enumerate(rows):
            for x, asset_id in enumerate(map(int, (row[i:i+2] for i in range(0, len(row), 2)))):
                if asset_id not in ALL_ASSET_IDS:
                    raise ValueError(f'Invalid tile id: {asset_id}')
                assets.append(ID_TO_ASSET[int(asset_id)](position=Position(x, y)))
        return cls(game=game, assets=assets)

    def set_line(self) -> None:
        assert not hasattr(self, 'line')
        self.line = '-'.join(''.join(str(next(a for a in self.assets if a.position == (x, y)).id).zfill(2) for x in range(self.dimensions[0])) for y in range(self.dimensions[1]))

    def in_bounds(self, position: Position) -> bool:
        return all(0 <= v < d for v, d in zip(position, self.dimensions))

    def tile(self, position: Position) -> Optional[Tile]:
        """Returns the tile at the given position, if the position is in bounds."""
        if not self.in_bounds(position):
            return None
        return self.tiles[position]

    def item(self, position: Position) -> Optional[Item]:
        """Returns the item at the given position, if any."""
        try:
            return next(item for item in self.items if item.position == position)
        except StopIteration:
            return None

    def __setitem__(self, position: Position, asset: Asset) -> None:
        asset.level = self
        asset.position = position
        if isinstance(asset, Tile):
            self.tiles[position] = asset
        elif isinstance(asset, Item):
            self.items.append(asset)
        else:
            raise TypeError(f'Expected Tile or Item, got {type(asset)}')

    def image(self) -> Image.Image:
        border: float = 0.50  # Width of transparant border around each side in percentage of TILE_SIZE
        top_multiplier: float = 1.0 / border
        image = Image.new(
            mode='RGBA',
            size=(
                int((self.dimensions[0] + border*2) * TILE_SIZE[0]),
                int((self.dimensions[1] + border + border*top_multiplier) * TILE_SIZE[1]),
            ),
            color=(0, 0, 0, 0),
        )

        def paste(asset: Optional[Asset] = None, im: Optional[Image.Image] = None, position: Optional[Position] = None) -> None:
            if asset is not None:
                im = asset.image()
                position =  asset.position
            else:
                assert im is not None and position is not None
            if not self.in_bounds(position):
                return
            image.paste(
                im=im,
                box=(
                    int((position.x + border) * TILE_SIZE[0] - TILE_OFFSET[0]),
                    int((position.y + border * top_multiplier) * TILE_SIZE[1] - TILE_OFFSET[1]),
                ),
                mask=im,
            )
        if self.game.thomas:  # type: ignore
            im = THOMAS.resize((TILE_SIZE[0] * self.dimensions[0], TILE_SIZE[1] * self.dimensions[1]))
            image.paste(
                im=im,
                box=(
                    int(border * TILE_SIZE[0]),
                    int((border * top_multiplier) * TILE_SIZE[1]),
                ),
                mask=im,
            )
        else:
            for x in range(self.dimensions[0]):
                for y in range(self.dimensions[1]):
                    paste(im=Empty.images[0], position=Position(x, y))

        for y in range(self.dimensions[1]):
            positions = [Position(x, y) for x in range(self.dimensions[0])]
            tiles = [self.tile(p) for p in positions]
            for tile in sorted(tiles, key=lambda t: (
                    isinstance(t, Solid),
                    isinstance(t, Walkable),
                )):
                assert tile is not None
                if not isinstance(tile, Empty):
                    paste(asset=tile)
            items = [self.item(p) for p in positions]
            for item in items:
                if item is not None:
                    paste(asset=item)
            if self.robbie.position.y == y:
                im = self.robbie.asset.image(position=self.robbie.position)
                if im is not None:
                    paste(im=im, position=self.robbie.position)
        n = 540
        image = image.resize((n, int(image.height / image.width * n)))
        return image

    def move(self, direction: Direction) -> bool:
        """Returns True if the move was successful, False otherwise."""
        if self.completed or self.failed:
            return False
        self.robbie.direction = direction
        position = self.robbie.position + direction.value
        if not self.in_bounds(position):
            return False
        tile = self.tile(position)
        now = self.tile(self.robbie.position)
        assert tile is not None and now is not None
        if not tile.can_enter() or not now.can_leave():
            return False
        item = self.item(position)
        if item is not None:
            if not item.can_enter():
                return False
            item.on_enter()
        tile.on_enter()
        self.robbie.position = position
        for asset in (*self.tiles.values(), *self.items):
            asset.after_every_move()
        if self.failed:
            self.game.tries_left -= 1
        self.moves += 1
        if self.started is None:
            self.started = time.time()
        return True

    def reset(self) -> None:
        level = Level.from_line(game=self.game, line=self.line)
        self.__dict__ = level.__dict__

    def retry(self) -> None:
        if not self.failed:
            self.game.tries_left -= 1
        self.reset()
