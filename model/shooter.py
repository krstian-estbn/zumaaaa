import math
from typing import List
import pyxel

from utils import Color
from .constants import RNG, COLORS
from .helper import rect_overlap

class Shooter:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.angle: float = 270
        self.color: Color = RNG.choice(COLORS)
        self.next_color: Color = RNG.choice(COLORS)
        self.bullets: List[Bullet] = []
        self.timer: float = 0
        self.rate: float = 0.9 / 30
        self.speed: float = pyxel.height / (5.0 * 30)

    def update(self) -> None:
        self.timer += self.rate
        for bullet in self.bullets[:]: # so walang maskip na bullets when removing
            if bullet.x <= 0 or bullet.y <= 0:
                self.bullets.remove(bullet)

    def shoot_bullet(self, angle: float) -> None:
        if self.timer >= 1 or not self.bullets:
            self.timer = 0
            self.bullets.append(
                Bullet(self.color, pyxel.width // 2 - 4, pyxel.height // 2 - 4, 4, angle, self.speed))
            self.color = self.next_color
            self.next_color = RNG.choice(COLORS)

    def edit_orientation(self, angle: float) -> None:
        self.angle = angle
    
    def change_color(self) -> None:
        self.color = self.next_color
        self.next_color = RNG.choice(COLORS)

class Bullet:
    def __init__(self, color: Color, x: int, y: int, r: int, angle_deg: float, speed: float):
        self.color: Color = color
        self.x: float = x
        self.y: float = y
        self.r: int = r

        angle = math.radians(angle_deg)
        self.dx: float = math.cos(angle) * speed
        self.dy: float = math.sin(angle) * speed

    def adjust_position(self) -> None:
        self.x += self.dx
        self.y += self.dy

    def collides(self, ax: int, ay: int, ar: int,
                 bx: int, by: int, br: int) -> bool:
        return rect_overlap(ax, ay, ar, bx, by, br)