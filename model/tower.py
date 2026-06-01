from typing import List
import pyxel

from utils import Color, Orientation
from .constants import RNG, COLORS
from .helper import rect_overlap

class Tower:
    def __init__(self, x: int, y: int, rate: float, speed: float):
        self.x: int = x
        self.y: int = y
        self.orientation: Orientation = Orientation.UP
        self.bullets: List[TowerBullet] = []
        self.show_info: bool = False
        self.level: int = 1
        self.timer: float = 0
        self.rate: float = rate / 30
        self.speed: float = pyxel.height / (speed * 30)

    def shoot_bullets(self) -> None:
        self.timer += self.rate
        if self.timer >= 1 or not self.bullets:
            self.timer = 0
            self.bullets.append(
                TowerBullet(self.x + 4, self.y + 4, 4, self.orientation, self.speed))

    def edit_orientation(self, orientation: Orientation) -> None:
        self.orientation = orientation

    def upgrade(self) -> None:
        self.level += 1
        self.rate += 0.2 / 30


class TowerBullet:
    def __init__(self, x: int, y: int, r: int, orientation: Orientation, speed: float):
        self.x: float = float(x)
        self.y: float = float(y)
        self.r: int = r
        self.speed: float = speed
        self.color: Color = RNG.choice(COLORS)
        self.orientation: Orientation = orientation
    
    def adjust_position(self) -> None:
        if self.orientation == Orientation.UP:
            self.y -= self.speed
        elif self.orientation == Orientation.DOWN:
            self.y += self.speed
        elif self.orientation == Orientation.RIGHT:
            self.x += self.speed
        else:
            self.x -= self.speed
    
    def collides(self, ax: int, ay: int, ar: int,
                 bx: int, by: int, br: int) -> bool:
        return rect_overlap(ax, ay, ar, bx, by, br)