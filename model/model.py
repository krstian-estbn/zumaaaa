import json
from typing import List, Tuple, Set, Optional, Dict

import pyxel

from .constants import RNG, Vec2, RouteNode
from .tower import Tower
from .shooter import Shooter
from .enemy import Enemy, Chameleon, Regenerator
from .helper import in_rect
from utils import GameState, Mode, create_grid


# 1 = right, 2 = up, 3 = down
class Model:
    DEFAULT_SETTINGS: Dict[str, int | float] = {
        "smooth": 1,
        "n_enemies": 5,
        "n_lives": 2,
        "enemy_speed": 2.0,
        "shooter_rate": 0.9,
        "shooter_speed": 5.0,
        "tower_rate": 0.5,
        "tower_speed": 5.0,
        "regen_h": 5.0,
        "cham_freq": 3.0
    }
    
    def __init__(self):
        self.settings: Dict[str, int | float] = self.load_settings()

        self.grid: list[tuple[int, int]] = create_grid(16, pyxel.height, pyxel.width)

        self.state: GameState = GameState.START
        
        self.smooth_int: int | float = self.settings["smooth"]
        self.smooth: bool = self.smooth_int == 1 # defaulted to be smooth
        
        self.mode: Optional[Mode] = None

        self.game_over: bool = False
        self.exp: int = 0
        self.lives: int | float = self.settings["n_lives"]
        self.limit: int | float = self.settings["n_enemies"]
        
        self.enemies: List[Enemy] = []
        
        self.enemy_speed: float = self.settings["enemy_speed"]
        self.regen_h: float = self.settings["regen_h"]
        self.cham_freq: float = self.settings["cham_freq"]
        self.hit_enemy: bool = False

        self.shooter: Shooter = Shooter(pyxel.width // 2, pyxel.height // 2)
        self.shooter_rate: float = self.settings["shooter_rate"]
        self.shooter_speed: float = self.settings["shooter_speed"]

        self.towers: List[Tower] = []
        self.tower_rate: float = self.settings["tower_rate"]
        self.tower_speed: float = self.settings["tower_speed"]
        
        self.spawn_interval: float = 1 / (self.enemy_speed * 30)
        self.timer: float = 0
        
        self.blocked_cells: Set[Vec2] = {(pyxel.width // 2 - 8, pyxel.height // 2 - 8)}
        self.tower_cells: Set[Vec2] = set()
        self.tunnel_cells: Set[Vec2] = set()

        self.routes: List[List[RouteNode]] = self.generate_routes()
        self.tunnels: List[List[RouteNode]] = self.generate_tunnels()
        
        self.start_round: bool = True
        self.rounds: int = 12
        self.rounds_survived: int = 0

        self.player_name: str = ""
        
    @property
    def is_game_over(self) -> bool:
        return self.game_over

    
    def end_game(self) -> None:
        if self.state in (GameState.NAME_INPUT, GameState.GAME_OVER):
            return
        self.state = GameState.NAME_INPUT
    
    def restart_game(self) -> None:
        self.__init__() # for play again

    def reset_round(self) -> None:
        self.rounds_survived += 1
        
        if self.mode in (Mode.CAMPAIGN_HARD, Mode.ENDLESS_HARD):
            self.blocked_cells = {(pyxel.width // 2 - 8, pyxel.height // 2 - 8)} | self.tower_cells
            self.tunnel_cells = set()
            self.routes = self.generate_routes()
            self.tunnels = self.generate_tunnels()
            
            for tower in self.towers:
                self.exp += tower.level * 5
                
            self.towers = []

        self.limit: int | float = self.settings["n_enemies"]
        self.enemies: List[Enemy] = []
        self.timer: float = 0
        self.start_round = True

        if self.lives <= 0:
            self.end_game()
        
        if self.mode in (Mode.CAMPAIGN_HARD, Mode.CAMPAIGN_NORMAL):
            self.rounds -= 1
            if self.rounds <= 0:
                self.end_game()

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

    def _enemy_in_tunnel(self, enemy: Enemy) -> bool:
        for tx, ty in self.tunnel_cells:
            if in_rect(enemy.x, enemy.y, tx, ty):
                return True

            if in_rect(enemy.x + enemy.r, enemy.y + enemy.r, tx, ty):
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
                                   int(enemy.x), int(enemy.y), enemy.r):

                    if bullet.color == enemy.color and not self._enemy_in_tunnel(enemy):
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
                    if bullet.collides(int(bullet.x), int(bullet.y), bullet.r,
                                       int(enemy.x), int(enemy.y), enemy.r):

                        if bullet.color == enemy.color and not self._enemy_in_tunnel(enemy):
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

        if self.lives <= 0:
            self.end_game()
            return
            
        if self.limit <= 0:
            self.reset_round()
            
    # configurations for settings
    def set_config(self, key: str, value: float) -> None:
        if key == "limit":
            self.limit = max(1, int(value))

        elif key == "lives":
            self.lives = max(1, int(value))

        elif key == "shooter_rate":
            self.shooter_rate = value
            self.shooter.rate = value / 30

        elif key == "shooter_speed":
            self.shooter_speed = value
            self.shooter.speed = pyxel.height / (value * 30)

        elif key == "tower_rate":
            self.tower_rate = value

        elif key == "tower_speed":
            self.tower_speed = value

        elif key == "enemy_speed":
            self.enemy_speed = value
            self.spawn_interval = 1 / (value * 30)

        elif key == "smooth":
            self.smooth_int = (self.smooth_int + 1) % 2
            self.smooth = self.smooth_int == 1

    def load_settings(self) -> Dict[str, int | float]:
        try:
            with open("settings.json", "r") as f:
                data: Dict[str, int | float] = json.load(f)
        except FileNotFoundError:
            data: Dict[str, int | float] = {}
        
        merged_settings = self.DEFAULT_SETTINGS.copy()
        merged_settings.update(data)
        return merged_settings

        
    def save_settings(self) -> None:
        self.settings.update({
            "smooth": self.smooth_int,
            "n_enemies": self.limit,
            "n_lives": self.lives,
            "enemy_speed": self.enemy_speed,
            "shooter_rate": self.shooter_rate,
            "shooter_speed": self.shooter_speed,
            "tower_rate": self.tower_rate,
            "tower_speed": self.tower_speed,
            "regen_h": self.regen_h,
            "cham_freq": self.cham_freq,
        })


        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=4)
