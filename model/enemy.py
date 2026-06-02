from typing import List

from utils import Color
from .constants import RNG, COLORS, RouteNode

class Enemy:
    def __init__(self, x: int, y: int, r: int, route: int, speed: float):
        self.x: float = float(x)
        self.y: float = float(y)
        self.r: int = r
        self.route: int = route
        self.route_idx: int = 0
        self.timer: float = 0.0
        self.speed: float = speed / (2.0 * 30)
        self.smooth_speed: float = 16 * self.speed
        self.spawned: bool = True
        self.hit_point: int = 1
        self.color: Color = RNG.choice(COLORS)

    def move(self, route: List[RouteNode], smooth: bool) -> None:
        node = route[self.route_idx]
        direction = node["direction"]

        self.timer += self.speed

        if smooth: # add: configurable speed for smooth movement
            self.spawned = False
            if direction == 1:
                self.x += self.smooth_speed
                if self.x >= node["x"]:
                    self.route_idx += 1

            elif direction == 2:
                self.y -= self.smooth_speed
                if self.y <= node["y"]:
                    self.route_idx += 1

            else:
                self.y += self.smooth_speed
                if self.y >= node["y"]:
                    self.route_idx += 1

        else:
            if self.timer >= 1:
                self.spawned = False
                self.timer = 0
                if direction == 1:
                    self.x = node["x"]
                    self.route_idx += 1
                
                elif direction == 2:
                    self.y = node["y"]
                    self.route_idx += 1
                
                else:
                    self.y = node["y"]
                    self.route_idx += 1

class Regenerator(Enemy):
    def __init__(self, h: float, x: int, y: int, r: int, route: int, speed: float):
        super().__init__(x, y, r, route, speed)
        self.h: float = h   
        self.acc: float = 16    

    def move(self, route: List[RouteNode], smooth: bool) -> None:
        node = route[self.route_idx]
        direction = node["direction"]

        self.timer += self.speed

        if smooth: # add: configurable speed for smooth movement
            self.spawned = False
            self.acc += self.smooth_speed
            if self.acc >= self.h * 16:
                self.acc = 0
                self.hit_point += 1
          
            if direction == 1:
                self.x += self.smooth_speed
                if self.x >= node["x"]:
                    self.route_idx += 1

            elif direction == 2:
                self.y -= self.smooth_speed
                if self.y <= node["y"]:
                    self.route_idx += 1

            else:
                self.y += self.smooth_speed
                if self.y >= node["y"]:
                    self.route_idx += 1

        else:
            if self.timer >= 1:
                self.spawned = False
                self.timer = 0
                if (self.route_idx + 1) % self.h == 0:
                    self.hit_point += 1

                if direction == 1:
                    self.x = node["x"]
                    self.route_idx += 1
                
                elif direction == 2:
                    self.y = node["y"]
                    self.route_idx += 1
                
                else:
                    self.y = node["y"]
                    self.route_idx += 1


class Chameleon(Enemy):
    def __init__(self, freq: float, x: int, y: int, r: int, route: int, speed: float):
        super().__init__(x, y, r, route, speed)
        self.freq: float = 1 / (freq * 30)
        self.freq_timer: float = 0

    def move(self, route: List[RouteNode], smooth: bool) -> None:
        node = route[self.route_idx]
        direction = node["direction"]

        self.timer += self.speed
        self.freq_timer += self.freq

        if self.freq_timer >= 1:
            self.freq_timer = 0
            self.color = RNG.choice(COLORS)

        if smooth: # add: configurable speed for smooth movement
            self.spawned = False
            if direction == 1:
                self.x += self.smooth_speed
                if self.x >= node["x"]:
                    self.route_idx += 1

            elif direction == 2:
                self.y -= self.smooth_speed
                if self.y <= node["y"]:
                    self.route_idx += 1

            else:
                self.y += self.smooth_speed
                if self.y >= node["y"]:
                    self.route_idx += 1

        else:
            if self.timer >= 1:
                self.spawned = False
                self.timer = 0
                if direction == 1:
                    self.x = node["x"]
                    self.route_idx += 1
                
                elif direction == 2:
                    self.y = node["y"]
                    self.route_idx += 1
                
                else:
                    self.y = node["y"]
                    self.route_idx += 1
