import json
import math
from random import Random
from typing import List, Tuple, Dict, Set, Optional

import pyxel

from utils import Color, Orientation, GameState, Mode, create_grid, overlap

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
    def __init__(self, x: int, y: int, r: int, route: int, speed: float):
        self.x: int = x
        self.y: int = y
        self.r: int = r
        self.route: int = route
        self.route_idx: int = 0
        self.timer: float = 0.0
        self.speed: float = 1 / (speed * 30)
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
                self.x += .5
                if self.x >= node["x"]:
                    self.route_idx += 1

            elif direction == 2:
                self.y -= .5
                if self.y <= node["y"]:
                    self.route_idx += 1

            else:
                self.y += .5
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
    def __init__(self, h: float, *args):
        super().__init__(*args)
        self.h: float = h
        self.smooth_speed: float = 0.5
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
    def __init__(self, freq: float, *args):
        super().__init__(*args)
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
                self.x += .5
                if self.x >= node["x"]:
                    self.route_idx += 1

            elif direction == 2:
                self.y -= .5
                if self.y <= node["y"]:
                    self.route_idx += 1

            else:
                self.y += .5
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
        self.x: int = x
        self.y: int = y
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
        self.speed: float = pyxel.height / (5 * 30)

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

# 1 = right, 2 = up, 3 = down

class Model:
    def __init__(self):
        with open('settings.json', 'r') as f:
            data = json.load(f)

        self.grid: list[tuple[int, int]] = create_grid(16, pyxel.height, pyxel.width)

        self.state: GameState = GameState.START
        self.smooth: bool = False
        self.mode: Optional[Mode] = None

        self.game_over: bool = False
        self.exp: int = 5
        self.lives: int = data["n_lives"]

        self.limit: int = data["n_enemies"]
        self.enemies: List[Enemy] = []
        self.enemy_speed: float = 2.0
        self.regen_h: float = 5
        self.cham_freq: float = 3.0
        self.hit_enemy: bool = False

        self.shooter: Shooter = Shooter(pyxel.width // 2, pyxel.height // 2)
        self.shooter_rate: float = 0.9
        self.shooter_speed: float = 5.0

        self.towers: List[Tower] = []
        self.tower_rate: float = 0.5
        self.tower_speed: float = 5.0
        
        self.spawn_interval: float = 1 / (2.0 * 30)
        self.timer: float = 0
        
        self.blocked_cells: Set[Vec2] = {(pyxel.width // 2 - 8, pyxel.height // 2 - 8)}
        self.tower_cells: Set[Vec2] = set()
        self.tunnel_cells: Set[Vec2] = set()

        self.routes: List[List[RouteNode]] = self.generate_routes()
        self.tunnels: List[List[RouteNode]] = self.generate_tunnels()
        
        self.start_round: bool = True
        self.rounds: int = 2

    @property
    def is_game_over(self) -> bool:
        return self.game_over

    def reset_round(self) -> None:
        with open('settings.json', 'r') as f:
            data = json.load(f)

        if self.mode in (Mode.CAMPAIGN_HARD, Mode.ENDLESS_HARD):
            self.blocked_cells = {(pyxel.width // 2 - 8, pyxel.height // 2 - 8)} | self.tower_cells
            self.tunnel_cells = set()
            self.routes = self.generate_routes()
            self.tunnels = self.generate_tunnels()
            for tower in self.towers:
                self.exp += tower.level * 5
            self.towers = []

        self.limit: int = data["n_enemies"]
        self.enemies: List[Enemy] = []
        self.timer: float = 0

        self.start_round = True

        if self.lives <= 0:
            self.game_over = True
        
        if self.mode in (Mode.CAMPAIGN_HARD, Mode.CAMPAIGN_NORMAL):
            self.rounds -= 1
            if self.rounds <= 0:
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

    # add: should occupy at most 2 tunnels per path
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

    def generate_tunnels(self) -> List[List[RouteNode]]:
        return [self.create_tunnel(r) for r in self.routes]

    def _in_tunnel(self, x: float, y: float) -> bool:
        for tx, ty in self.tunnel_cells:
            if in_rect(x, y, tx, ty):
                return True
        return False

    # 1 = normal, 2 = regenerator, 3 = chameleon; 1/2 chance for normal, 1/4 chance for special
    def spawn_enemies(self) -> None:
        self.timer += self.spawn_interval

        if self.timer >= 1 and len(self.enemies) < self.limit:
            self.timer = 0
            route: int = RNG.randint(0, 1) if len(self.routes) == 2 else 0
            enemy_type = RNG.choice([1, 1, 2, 3])
            
            if enemy_type == 3:
                self.enemies.append(
                    Chameleon(
                        self.cham_freq, 
                        self.routes[route][0]["x"], 
                        self.routes[route][0]["y"], 
                        8, 
                        route, 
                        self.enemy_speed
                    )
                )
            
            elif enemy_type == 2:
                self.enemies.append(
                    Regenerator(
                        self.regen_h, 
                        self.routes[route][0]["x"], 
                        self.routes[route][0]["y"], 
                        8, 
                        route, 
                        self.enemy_speed
                    )
                )
            
            else:
                self.enemies.append(
                    Enemy(
                        self.routes[route][0]["x"], 
                        self.routes[route][0]["y"], 
                        8, 
                        route, 
                        self.enemy_speed
                    )
                )

    def place_tower(self, x: int, y: int) -> None:
        self.towers.append(Tower(x, y, self.tower_rate, self.tower_speed))

    def update(self) -> None:
        hit_bullets: Set[int] = set()
        hit_enemies: Set[int] = set()
        hit_tower_bullets: Set[Tuple[int, int]] = set()

        self.shooter.update()
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

            enemy.move(self.routes[enemy.route], self.smooth)

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
                        if enemy.hit_point <= 1:
                            hit_enemies.add(j)
                            self.hit_enemy = True
                            self.exp += 1
                            self.limit -= 1
                        else:
                            enemy.hit_point -= 1

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
                            if enemy.hit_point <= 1:
                                hit_enemies.add(j)
                                self.hit_enemy = True
                                self.exp += 1
                                self.limit -= 1
                            else:
                                enemy.hit_point -= 1

                        hit_tower_bullets.add((k, i))

        # cleanup
        self.shooter.bullets = [b for i, b in enumerate(self.shooter.bullets) if i not in hit_bullets]
        self.enemies = [e for i, e in enumerate(self.enemies) if i not in hit_enemies]

        for k, tower in enumerate(self.towers):
            tower.bullets = [b for i, b in enumerate(tower.bullets) if (k, i) not in hit_tower_bullets]

        if self.lives <= 0 or self.limit <= 0:
            self.reset_round()
