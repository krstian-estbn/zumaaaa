from enum import Enum, auto

class Color(Enum):
    YELLOW = auto()
    GREEN = auto()
    BLUE = auto()
    PINK = auto()
    WHITE = auto()

class Orientation(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class GameState(Enum):
    START = auto()
    GAME = auto()
    SETTINGS = auto()

class Mode(Enum):
    CAMPAIGN_NORMAL = auto()
    CAMPAIGN_HARD = auto()
    ENDLESS_NORMAL = auto()
    ENDLESS_HARD = auto()

def create_grid(cell_size: int, screen_height: int, screen_width: int) -> list[tuple[int, int]]:
    li: list[tuple[int, int]] = []
    for x in range(0, screen_width, cell_size):
        for y in range(0, screen_height, cell_size):
            li.append((x, y))
    return li

def overlap(int1: tuple[int, int], int2: tuple[int, int]) -> bool:
    l1, r1 = int1
    l2, r2 = int2

    return max(l1, l2) <= min(r1, r2)

