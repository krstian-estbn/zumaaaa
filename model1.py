import math
from random import Random
from typing import List, Tuple, Dict, Set

import pyxel

from utils import Color, Orientation, create_grid, overlap

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


# helper stuff
def rect_overlap(ax: int, ay: int, ar: int,
                 bx: int, by: int, br: int) -> bool:
    return overlap((ax, ax + ar * 2), (bx, bx + br * 2)) and overlap(
        (ay, ay + ar * 2), (by, by + br * 2)
    )


def in_rect(x: float, y: float, rx: int, ry: int, size: int = 16) -> bool:
    return rx <= x <= rx + size and ry <= y <= ry + size


class Enemy:
    def __init__(self, x: int, y: int, r: int, route: int):
        self.x: int = x
        self.y: int = y
        self.r: int = r
        self.route: int = route
        self.route_idx: int = 0
        self.color: Color = RNG.choice(COLORS)

    def move(self, route: List[RouteNode]) -> None:
        node = route[self.route_idx]
        direction = node["direction"]

        if direction == 1:
            self.x += 1
            if self.x >= node["x"]:
                self.route_idx += 1

        elif direction == 2:
            self.y -= 1
            if self.y <= node["y"]:
                self.route_idx += 1

        else:
            self.y += 1
            if self.y >= node["y"]:
                self.route_idx += 1

class Bullet:
    def __init__(self, color: Color, x: int, y: int, r: int, angle_deg: float, speed: float = 8):
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

class Tower:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.orientation: Orientation = Orientation.UP
        self.bullets: List[TowerBullet] = []
        self.level: int = 1
        self.timer: int = 0
        self.bullet_interval: int = 30

    def shoot_bullets(self):
        self.timer += 1
        if self.timer >= self.bullet_interval:
            self.timer = 0
            self.bullets.append(TowerBullet(self.x + 4, self.y + 4, 4, self.orientation))

class TowerBullet:
    def __init__(self, x: int, y: int, r: int, orientation: Orientation):
        self.x: int = x
        self.y: int = y
        self.r: int = r
        self.color: Color = RNG.choice(COLORS)
        self.orientation: Orientation = orientation
        self.bullet_speed: int = 8

    def adjust_position(self) -> None:
        if self.orientation == Orientation.UP:
            self.y -= self.bullet_speed
        elif self.orientation == Orientation.DOWN:
            self.y += self.bullet_speed
        elif self.orientation == Orientation.RIGHT:
            self.x += self.bullet_speed
        else:
            self.x -= self.bullet_speed

    def collides(self, ax: int, ay: int, ar: int,
                 bx: int, by: int, br: int) -> bool:
        return rect_overlap(ax, ay, ar, bx, by, br)
       
class Shooter:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.angle: float = 270
        self.color: Color = RNG.choice(COLORS)
        self.next_color: Color = RNG.choice(COLORS)
        self.bullets: List[Bullet] = []

    def shoot_bullet(self, angle: float) -> None:
        self.bullets.append(
            Bullet(self.color, pyxel.width // 2 - 4, pyxel.height // 2 - 4, 4, angle))
        self.color = self.next_color
        self.next_color = RNG.choice(COLORS)
        
    def edit_orientation(self, angle: float):
        self.angle = angle
        
    def change_color(self):
        self.color = self.next_color
        self.next_color = RNG.choice(COLORS)

# 1 = right, 2 = up, 3 = down

class Model:
    def __init__(self):
        self.grid: list[tuple[int, int]] = create_grid(16, pyxel.height, pyxel.width)
        
        self.game_over: bool = False
        self.exp: int = 0
        self.lives: int = 2

        self.limit: int = 5
        self.enemies: List[Enemy] = []
        self.towers: List[Tower] = []
        
        self.timer: int = 0
        self.spawn_interval: int = 50
        
        self.shooter = Shooter(pyxel.width // 2, pyxel.height // 2)

        self.blocked_cells: Set[Vec2] = {(pyxel.width // 2 - 8, pyxel.height // 2 - 8)}
        self.tower_cells: Set[Vec2] = set()
        self.tunnel_cells: Set[Vec2] = set()
        
        self.routes: List[List[RouteNode]] = self.generate_routes()
        self.tunnels = self.generate_tunnels()

        self.start_round: bool = True
        self.rounds: int = 2

    @property
    def is_game_over(self):
        return self.game_over
    
    def reset_round(self) -> None:
        self.limit: int = 5
        self.enemies: List[Enemy] = []
        self.timer: int = 0

        self.blocked_cells = {(pyxel.width // 2 - 8, pyxel.height // 2 - 8)} | self.tower_cells
        self.routes = self.generate_routes()
        self.tunnels = self.generate_tunnels()

        self.start_round = True
        self.rounds -= 1

        if self.lives <= 0 or self.rounds <= 0:
            self.game_over = True
            
    def generate_routes(self) -> List[List[RouteNode]]:
        cell_size = 16
        padding = 32

        center_y = pyxel.height // 2 - 8

        upper_min, upper_max = padding, center_y - padding
        lower_min, lower_max = center_y + padding, pyxel.height - padding - cell_size

        def walk_route(start_y: int, min_y: int, max_y: int) -> List[RouteNode]:
            route: List[RouteNode] = [
                {"direction": 1, "x": 0, "y": start_y},
                {"direction": 1, "x": 16, "y": start_y},
            ]

            self.blocked_cells.add((0, start_y))
            self.blocked_cells.add((16, start_y))

            while route[-1]["x"] + cell_size < pyxel.width:
                last = route[-1]

                choices = [
                    {"direction": 1, "x": last["x"] + cell_size, "y": last["y"]},
                ]

                if last["direction"] != 3 and last["y"] - cell_size >= min_y:
                    choices.append({"direction": 2, "x": last["x"], "y": last["y"] - cell_size})

                if last["direction"] != 2 and last["y"] + cell_size <= max_y:
                    choices.append({"direction": 3, "x": last["x"], "y": last["y"] + cell_size})

                valid = [c for c in choices if (c["x"], c["y"]) not in self.blocked_cells]

                next_node = RNG.choice(valid) if valid else choices[0]

                route.append(next_node)
                self.blocked_cells.add((next_node["x"], next_node["y"]))

            return route

        routes: List[List[RouteNode]] = []

        if RNG.randint(1, 2) == 2:
            y1 = RNG.choice([y for _, y in self.grid if upper_min <= y <= upper_max])
            y2 = RNG.choice([y for _, y in self.grid if lower_min <= y <= lower_max])

            routes.append(walk_route(y1, upper_min, upper_max))
            routes.append(walk_route(y2, lower_min, lower_max))
        else:
            y = RNG.choice([y for x, y in self.grid if x == 0])

            if y <= upper_max:
                routes.append(walk_route(y, upper_min, upper_max))
            else:
                routes.append(walk_route(y, lower_min, lower_max))

        return routes
    
    def create_tunnel(self, route: List[RouteNode]) -> List[RouteNode]:
        length: int = len(route)
        size: int = RNG.randint(2, 5)

        start: int = RNG.randint(0, length - size)

        tunnel: List[RouteNode] = []
        for i in range(start, start + size):
            node = route[i]
            self.tunnel_cells.add((node["x"], node["y"]))
            tunnel.append(node)

        return tunnel

    def generate_tunnels(self):
        return [self.create_tunnel(r) for r in self.routes]


    def _in_tunnel(self, x: float, y: float) -> bool:
        for tx, ty in self.tunnel_cells:
            if in_rect(x, y, tx, ty):
                return True
        return False
            
    def spawn_enemies(self) -> None:
        self.timer += 1

        if self.timer >= self.spawn_interval and len(self.enemies) < self.limit:
            self.timer = 0
            route: int = RNG.randint(0, 1) if len(self.routes) == 2 else 0

            self.enemies.append(
                Enemy(
                    self.routes[route][0]["x"],
                    self.routes[route][0]["y"],
                    8,
                    route,
                )
            )
    
    def place_tower(self, x: int, y: int):
        self.towers.append(Tower(x, y))
        
    def update(self) -> None:
        hit_bullets: Set[int] = set()
        hit_enemies: Set[int] = set()
        hit_tower_bullets: Set[Tuple[int, int]] = set()

        self.spawn_enemies()

        for tower in self.towers:
            tower.shoot_bullets()

        # enemies
        for enemy in self.enemies[:]:
            if enemy.route_idx >= len(self.routes[enemy.route]):
                self.enemies.remove(enemy)
                self.lives -= 1
                self.limit -= 1
                continue

            enemy.move(self.routes[enemy.route])

        # shooter bullets
        for i, bullet in enumerate(self.shooter.bullets):
            bullet.adjust_position()

            if self._in_tunnel(bullet.x, bullet.y):
                hit_bullets.add(i)
                continue

            for j, enemy in enumerate(self.enemies):
                if bullet.collides(int(bullet.x), int(bullet.y), bullet.r,
                                   enemy.x, enemy.y, enemy.r):

                    if bullet.color == enemy.color and not self._in_tunnel(enemy.x, enemy.y):
                        hit_enemies.add(j)
                        self.exp += 1
                        self.limit -= 1

                    hit_bullets.add(i)

        # tower bullets
        for k, tower in enumerate(self.towers):
            for i, bullet in enumerate(tower.bullets):
                bullet.adjust_position()

                if self._in_tunnel(bullet.x, bullet.y):
                    hit_tower_bullets.add((k, i))
                    continue

                for j, enemy in enumerate(self.enemies):
                    if bullet.collides(bullet.x, bullet.y, bullet.r,
                                       enemy.x, enemy.y, enemy.r):

                        if bullet.color == enemy.color and not self._in_tunnel(enemy.x, enemy.y):
                            hit_enemies.add(j)
                            self.exp += 1
                            self.limit -= 1

                        hit_tower_bullets.add((k, i))

        # cleanup
        self.shooter.bullets = [b for i, b in enumerate(self.shooter.bullets) if i not in hit_bullets]
        self.enemies = [e for i, e in enumerate(self.enemies) if i not in hit_enemies]

        for k, tower in enumerate(self.towers):
            tower.bullets = [b for i, b in enumerate(tower.bullets) if (k, i) not in hit_tower_bullets]

        if self.lives == 0 or self.limit <= 0:
            self.reset_round()