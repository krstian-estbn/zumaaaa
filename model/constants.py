from random import Random
from typing import List, Tuple, Dict

from utils import Color

RNG = Random()

COLORS: List[Color] = [
    Color.PINK,
    Color.YELLOW,
    Color.BLUE,
    Color.WHITE,
    Color.GREEN,
]

Vec2 = Tuple[int, int]
RouteNode = Dict[str, int]