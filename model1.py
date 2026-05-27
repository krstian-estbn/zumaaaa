import enum
from random import Random
from utils import Color, Orientation, create_grid, overlap

import pyxel
import math

RNG = Random()

COLORS = [Color.PINK, Color.YELLOW, Color.BLUE, Color.WHITE, Color.GREEN]


class Enemy:
    def __init__(self, x: int, y: int, r: int, route: int):
        self.color = RNG.choice(COLORS)
        self.x = x
        self.y = y
        self.r = r
        self.route = route
        self.route_idx = 0

    def move(self, route):
        curr_idx = self.route_idx

        if route[curr_idx]["direction"] == 1:
            self.x += 1
            if self.x >= route[curr_idx]["x"]:
                self.route_idx += 1
        elif route[curr_idx]["direction"] == 2:
            self.y -= 1
            if self.y <= route[curr_idx]["y"]:
                self.route_idx += 1
        else:
            self.y += 1
            if self.y >= route[curr_idx]["y"]:
                self.route_idx += 1

class Bullet:
    def __init__(self, color: Color, x: int, y: int, r: int, angle_deg, speed=8):
        self.color = color
        self.x = x
        self.y = y
        self.r = r

        angle_rad = math.radians(angle_deg)
        self.dx = math.cos(angle_rad) * speed
        self.dy = math.sin(angle_rad) * speed

    def adjust_position(self):
        self.x += self.dx
        self.y += self.dy

    def collide_with_enemy(self, ax: int, ay: int, ar: int, bx: int, by: int, br: int) -> bool:
        bullet_xint = (ax, ax + ar * 2)
        enemy_xint = (bx, bx + br * 2)
        bullet_yint = (ay, ay + ar * 2)
        enemy_yint = (by, by + br * 2)
        
        return (overlap(bullet_xint, enemy_xint) and overlap(bullet_yint, enemy_yint))

class Tower:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.orientation = Orientation.UP
        self.bullets = []
        self.show_info = False
        self.level = 1
        self.timer = 0
        self.bullet_interval = 30

    def shoot_bullets(self):
        self.timer += 1
        if self.timer >= self.bullet_interval:
            self.timer = 0
            self.bullets.append(TowerBullet(self.x + 4, self.y + 4, 4, self.orientation))

    def edit_orientation(self, orientation):
        self.orientation = orientation

    def upgrade(self):
        self.level += 1
        self.bullet_interval -= 5


class TowerBullet:
    def __init__(self, x, y, r, orientation):
        self.x = x
        self.y = y
        self.r = r
        self.color = RNG.choice(COLORS)
        self.orientation = orientation
    
    def adjust_position(self):
        if self.orientation == Orientation.UP:
            self.y -= 8
        elif self.orientation == Orientation.DOWN:
            self.y += 8
        elif self.orientation == Orientation.RIGHT:
            self.x += 8
        else:
            self.x -= 8
    
    def collide_with_enemy(self, ax: int, ay: int, ar: int, bx: int, by: int, br: int) -> bool:
        bullet_xint = (ax, ax + ar * 2)
        enemy_xint = (bx, bx + br * 2)
        bullet_yint = (ay, ay + ar * 2)
        enemy_yint = (by, by + br * 2)
        
        return (overlap(bullet_xint, enemy_xint) and overlap(bullet_yint, enemy_yint))

class Shooter:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.angle = 270
        self.color = RNG.choice(COLORS)
        self.next_color = RNG.choice(COLORS)
        self.bullets = []

    def change_color(self):
        self.color = self.next_color
        self.next_color = RNG.choice(COLORS)

    def shoot_bullet(self, angle):
        self.bullets.append(Bullet(self.color, pyxel.width // 2 - 4, pyxel.height // 2 - 4, 4, angle))
        self.color = self.next_color
        self.next_color = RNG.choice(COLORS)

    def edit_orientation(self, angle):
        self.angle = angle

# 1 = right, 2 = up, 3 = down

class Model:
    def __init__(self):
        self.grid = create_grid(16, pyxel.height, pyxel.width)
        self.game_over = False
        self.exp = 15 # 15 for testing, but 0 default
        self.lives = 2

        self.limit = 5
        self.enemies = []
        self.timer = 0
        self.spawn_interval = 50
        self.towers = []
        self.shooter = Shooter(pyxel.width // 2, pyxel.height // 2)
        
        self.blocked_cells = {(pyxel.width // 2 - 8, pyxel.height // 2 - 8)}
        self.tower_cells = set()
        self.tunnel_cells = set()
        self.routes = self.generate_routes()
        self.tunnels = self.generate_tunnels()
        
        self.start_round = True
        self.rounds = 2

    @property
    def is_game_over(self):
        return self.game_over

    def reset_round(self):
        self.limit = 5
        self.enemies = []
        self.timer = 0

        self.blocked_cells = {(pyxel.height // 2 - 8, pyxel.width // 2 - 8)} | self.tower_cells
        self.routes = self.generate_routes()
        self.tunnels = self.generate_tunnels()

        self.start_round = True
        self.rounds -= 1

        if self.lives == 0 or self.rounds == 0:
            self.game_over = True

    def create_tunnel(self, route):
        no_of_tunnels = RNG.randint(1, 2)

        if no_of_tunnels == 1:
            while True:
                len_tunnel = RNG.randint(2, 5)
                if len_tunnel <= len(route) // 2:
                    break

            starting_tunnel = RNG.randint(0, len(route) - len_tunnel)

            tunnel = []
            
            for i in range(starting_tunnel, starting_tunnel + len_tunnel):
                self.tunnel_cells.add((route[i]["x"], route[i]["y"]))
                tunnel.append({"direction": route[i]["direction"], "x": route[i]["x"], "y": route[i]["y"]})

            return tunnel
        else:
            while True:
                len_tunnel1 = RNG.randint(2, 5)
                len_tunnel2 = RNG.randint(2, 5)
                if len_tunnel1 + len_tunnel2 <= len(route) // 2:
                    starting_tunnel1 = RNG.randint(0, len(route) - len_tunnel1)

                    before_end = starting_tunnel1 - len_tunnel2 - 1
                    after_start = starting_tunnel1 + len_tunnel1 + 1
                    after_end = len(route) - len_tunnel2

                    starting_tunnel2_candidates = []

                    if before_end >= 0:
                        starting_tunnel2_candidates.append(RNG.randint(0, before_end))
                    if after_start <= after_end:
                        starting_tunnel2_candidates.append(RNG.randint(after_start, after_end))

                    if starting_tunnel2_candidates:
                        break

            starting_tunnel2 = RNG.choice(starting_tunnel2_candidates)

            tunnel = []

            for i in range(starting_tunnel1, starting_tunnel1 + len_tunnel1):
                self.tunnel_cells.add((route[i]["x"], route[i]["y"]))
                tunnel.append({"direction": route[i]["direction"], "x": route[i]["x"], "y": route[i]["y"]})

            for i in range(starting_tunnel2, starting_tunnel2 + len_tunnel2):
                self.tunnel_cells.add((route[i]["x"], route[i]["y"]))
                tunnel.append({"direction": route[i]["direction"], "x": route[i]["x"], "y": route[i]["y"]})

            return tunnel

    def generate_tunnels(self):
        ans = []
        for route in self.routes:
            ans.append(self.create_tunnel(route))
        return ans

    def generate_routes(self):
        cell_size = 16
        padding = 32

        center_cell_y = pyxel.height // 2 - 8

        upper_min_y = padding
        upper_max_y = center_cell_y - padding

        lower_min_y = center_cell_y + padding
        lower_max_y = pyxel.height - padding - cell_size

        no_of_routes = RNG.randint(1, 2)
        routes = []

        def walk_route(start_y, min_y, max_y):
            route = [
                {'direction': 1, 'x': 0, 'y': start_y},
                {'direction': 1, 'x': 16, 'y': start_y}
            ]
            self.blocked_cells.add((0, start_y))
            self.blocked_cells.add((16, start_y))

            while route[-1]['x'] + cell_size < pyxel.width:
                last = route[-1]
                choices = []

                choices.append({'direction': 1, 'x': last['x'] + cell_size, 'y': last['y']})

                if last['direction'] != 3 and last['y'] - cell_size >= min_y:
                    choices.append({'direction': 2, 'x': last['x'], 'y': last['y'] - cell_size})

                if last['direction'] != 2 and last['y'] + cell_size <= max_y:
                    choices.append({'direction': 3, 'x': last['x'], 'y': last['y'] + cell_size})

                valid_choices = [c for c in choices if (c['x'], c['y']) not in self.blocked_cells]

                if not valid_choices:
                    next_route = {'direction': 1, 'x': last['x'] + cell_size, 'y': last['y']}
                else:
                    next_route = RNG.choice(valid_choices)

                route.append(next_route)
                self.blocked_cells.add((next_route['x'], next_route['y']))

            return route

        if no_of_routes == 2:
            choices_upper = [y for x, y in self.grid if x == 0 and upper_min_y <= y <= upper_max_y and (0, y) not in self.blocked_cells]
            y1 = RNG.choice(choices_upper)
            routes.append(walk_route(y1, upper_min_y, upper_max_y))

            choices_lower = [y for x, y in self.grid if x == 0 and lower_min_y <= y <= lower_max_y and (0, y) not in self.blocked_cells]
            y2 = RNG.choice(choices_lower)
            routes.append(walk_route(y2, lower_min_y, lower_max_y))
        else:
            choices = [y for x, y in self.grid if x == 0 and ((upper_min_y <= y <= upper_max_y) or (lower_min_y <= y <= lower_max_y)) and (0, y) not in self.blocked_cells]
            y1 = RNG.choice(choices)
            if y1 <= upper_max_y:
                routes.append(walk_route(y1, upper_min_y, upper_max_y))
            else:
                routes.append(walk_route(y1, lower_min_y, lower_max_y))

        return routes

    def place_tower(self, x, y):
        self.towers.append(Tower(x, y))

    def spawn_enemies(self):
        self.timer += 1
        if self.timer >= self.spawn_interval and len(self.enemies) < self.limit:
            self.timer = 0
            route = RNG.randint(0, 1) if len(self.routes) == 2 else 0
            self.enemies.append(Enemy(self.routes[route][0]["x"], self.routes[route][0]["y"], 8, route))

    def update(self):
        hit_bullets = set()
        hit_enemies = set()
        hit_tower_bullets = set()

        def hit_bullet(bullet, enemy, i, j, k=None):
            if bullet.color == enemy.color and not in_tunnel(enemy.x, enemy.y):
                hit_enemies.add(j)
                self.exp += 1
                self.limit -= 1
            if k is not None:
                hit_tower_bullets.add((k, i))
            else:
                hit_bullets.add(i)

        def in_tunnel(x, y):
            for tx, ty in self.tunnel_cells:
                if tx <= x <= tx + 16 and ty <= y <= ty + 16:
                    return True
            return False

        self.spawn_enemies()

        for tower in self.towers:
            tower.shoot_bullets()

        for enemy in self.enemies:
            curr_idx = enemy.route_idx
            route = self.routes[enemy.route]

            if curr_idx >= len(route):
                self.enemies.remove(enemy)
                self.lives -= 1
                self.limit -= 1
                continue

            enemy.move(route)

        for i, bullet in enumerate(self.shooter.bullets):
            bullet.adjust_position()

            if in_tunnel(bullet.x, bullet.y):
                hit_bullets.add(i)
                break

            for j, enemy in enumerate(self.enemies):
                if bullet.collide_with_enemy(bullet.x, bullet.y, bullet.r, enemy.x, enemy.y, enemy.r):
                    hit_bullet(bullet, enemy, i, j)

        for k, tower in enumerate(self.towers):
            for i, bullet in enumerate(tower.bullets):
                bullet.adjust_position()

                if in_tunnel(bullet.x, bullet.y):
                    hit_tower_bullets.add((k, i))
                    break

                for j, enemy in enumerate(self.enemies):
                    if bullet.collide_with_enemy(bullet.x, bullet.y, bullet.r, enemy.x, enemy.y, enemy.r):
                        hit_bullet(bullet, enemy, i, j, k)

        self.shooter.bullets = [bullet for i, bullet in enumerate(self.shooter.bullets) if i not in hit_bullets]
        self.enemies = [enemy for i, enemy in enumerate(self.enemies) if i not in hit_enemies]

        for k, tower in enumerate(self.towers):
            tower.bullets = [bullet for i, bullet in enumerate(tower.bullets) if (k, i) not in hit_tower_bullets]

        if self.lives == 0 or self.limit <= 0:
            self.reset_round()
