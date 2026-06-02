from model.model import Model
from model.leaderboard import save_score
from model.enemy import Regenerator, Chameleon
from model.tower import Tower
from model.constants import RNG
from view import View
from utils import Orientation, GameState, Mode

import pyxel
import math
import json

N = 10
ENEMY_CELLS = [(0, 0), (16, 0), (32, 0), (48, 0), (0, 16), (0, 144), (16, 144), (32, 144), (48, 144), (0, 160), (0, 176), (16, 176), (32, 176), (48, 176), (0, 192), (64, 16), (16, 160), (16, 192)]

class Controller:
    def __init__(self, model: Model, view: View):
        self._model: Model = model
        self._view: View = view

        self.input: str = ""
        self.name_input: str = ""
        self.place_tower: bool = False
        self.select_tower: Tower = None
        self.orientation: bool = False
        self.upgrade: bool = False
        self.tx: int = 0
        self.ty: int = 0
        self.previous_state: GameState = None
        self.enemy_start: tuple[int, ...] = []

        self.leaderboard_state: str = 1
        self.leaderboard_page: int = 1
        self.leaderboard_max_page: int = 0
        self.leaderboard_normal: list[list[dict[str, str | int]]] = []
        self.leaderboard_hard: list[list[dict[str, str | int]]] = []
        self.update_leaderboard()

    def start_game(self):
        pyxel.load("zuma.pyxres")
        pyxel.playm(1, 0, loop=True)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def take_input(self):
        if pyxel.btnp(pyxel.KEY_N):
            self.input = "N"
        elif pyxel.btnp(pyxel.KEY_Y):
            if self._model.exp >= 5:
                self.input = "Y"
        elif pyxel.btnp(pyxel.KEY_RETURN) and self.input != "":
            self.place_tower = True if self.input == "Y" else False
            self.input = ""
            self._model.start_round = False
        elif pyxel.btnp(pyxel.KEY_BACKSPACE) and self.input != "":
            self.input = ""
        else:
            pass

    def check_tower(self):
        blocked = False
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        self.tx = (mx // 16) * 16
        self.ty = (my // 16) * 16

        for x, y in (self._model.blocked_cells | self._model.tower_cells):
            if not (self.tx <= x < self.tx + 16 and self.ty <= y < self.ty + 16) and not (self.tx <= pyxel.width // 2 < self.tx + 16 and self.ty <= pyxel.height // 2 < self.ty + 16):
                continue
            else:
                blocked = True
                break

        if not blocked and self._model.exp >= 5:
            self._model.tower_cells.add((self.tx, self.ty))
            self._model.place_tower(self.tx, self.ty)
            self.orientation = False
            self._model.exp -= 5

    def edit_orientation(self):
        assert self.select_tower

        keys = {pyxel.KEY_W: Orientation.UP, pyxel.KEY_A: Orientation.LEFT, pyxel.KEY_S: Orientation.DOWN, pyxel.KEY_D: Orientation.RIGHT}

        for key, orientation in keys.items():
            if pyxel.btnp(key):
                self.select_tower.edit_orientation(orientation)
                self.orientation = False
                break
            else:
                pass

    def upgrade_tower(self):
        assert self.select_tower

        if self._model.exp >= 5:
            self.select_tower.upgrade()
            self._model.exp -= 5
        self.upgrade = False


    def _is_clicked_button(self, x: int, y: int, width=16, height=16) -> bool:
        return (x <= pyxel.mouse_x < x + width and y <= pyxel.mouse_y < y + height)

    def _is_clicked_text(self, x: int, y: int, len_text: int) -> bool:
        padding = 3
        text_width = len_text * 4 + padding * 2 + 2
        text_height = 6 + padding * 2 + 2
        return (
            x - text_width // 2 <= pyxel.mouse_x <= x + text_width // 2 and 
            y <= pyxel.mouse_y <= y + text_height
        )

    def update_leaderboard(self):
        try:
            with open("leaderboard.json", "r") as f:
                data: Dict[str, int | float] = json.load(f)
        except FileNotFoundError:
            data: Dict[str, int | float] = {}

        if self.leaderboard_state:
            data_normal = data["campaign_normal"]
            data_hard = data["campaign_hard"]
        else:
            data_normal = data["endless_normal"]
            data_hard = data["endless_hard"]

        self.leaderboard_normal = [data_normal[i:i+3] for i in range(0, len(data_normal), 3)]
        self.leaderboard_hard = [data_hard[i:i+3] for i in range(0, len(data_normal), 3)]

        self.leaderboard_max_page = max(math.ceil(len(self.leaderboard_normal)), math.ceil(len(self.leaderboard_hard)))

    def click_tower_info(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if self._is_clicked_button(110, pyxel.height - 30):
            self.orientation = True
        elif self._is_clicked_button(10, pyxel.height - 30):
            self.upgrade = True
        elif self._is_clicked_button(pyxel.width - 10 - 4, pyxel.height - 40, 4, 6):
            self.select_tower = None
        else:
            pass

    def take_name_input(self):
        key_map = {
        pyxel.KEY_A: "A", pyxel.KEY_B: "B", pyxel.KEY_C: "C", pyxel.KEY_D: "D",
        pyxel.KEY_E: "E", pyxel.KEY_F: "F", pyxel.KEY_G: "G", pyxel.KEY_H: "H",
        pyxel.KEY_I: "I", pyxel.KEY_J: "J", pyxel.KEY_K: "K", pyxel.KEY_L: "L",
        pyxel.KEY_M: "M", pyxel.KEY_N: "N", pyxel.KEY_O: "O", pyxel.KEY_P: "P",
        pyxel.KEY_Q: "Q", pyxel.KEY_R: "R", pyxel.KEY_S: "S", pyxel.KEY_T: "T",
        pyxel.KEY_U: "U", pyxel.KEY_V: "V", pyxel.KEY_W: "W", pyxel.KEY_X: "X",
        pyxel.KEY_Y: "Y", pyxel.KEY_Z: "Z",
        pyxel.KEY_0: "0", pyxel.KEY_1: "1", pyxel.KEY_2: "2", pyxel.KEY_3: "3",
        pyxel.KEY_4: "4", pyxel.KEY_5: "5", pyxel.KEY_6: "6", pyxel.KEY_7: "7",
        pyxel.KEY_8: "8", pyxel.KEY_9: "9",
        pyxel.KEY_SPACE: " ",
        }

        for key, char in key_map.items():
            if pyxel.btnp(key):
                if len(self.name_input) < 12:
                    self.name_input += char
                return

        if pyxel.btnp(pyxel.KEY_BACKSPACE) and self.name_input:
            self.name_input = self.name_input[:-1]

        if pyxel.btnp(pyxel.KEY_RETURN) and self.name_input.strip():
            self._model.player_name = self.name_input.strip()
            if self._model.mode is not None:
                save_score(self._model.mode, self._model.player_name, self._model.exp, self._model.rounds_survived)
            
            self._model.game_over = True
            self._model.state = GameState.GAME_OVER
            
    def update(self):
        if self._model.state == GameState.START:
            self.previous_state = GameState.START

            if pyxel.frame_count % 60 == 0:
                self.enemy_start = []
                for _ in range(N):
                    valid_cells = [(x, y) for x, y in self._model.grid if not (32 <= x <= 160 and 48 <= y <= 96) and not (64 <= x <= 128 and 112 <= y <= 160)]
                    x, y = RNG.choice(valid_cells)
                    u, v = RNG.choice(ENEMY_CELLS)
                    self.enemy_start.append((x, y, u, v))

            max_y = pyxel.height // 2 - 51 + 60
            spacing = 16
            text_len = 14
            if pyxel.btnp(pyxel.KEY_P) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y, text_len)):
                self._model.state = GameState.GAME
            elif pyxel.btnp(pyxel.KEY_S) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y + spacing, text_len)):
                self._model.state = GameState.SETTINGS
            elif pyxel.btnp(pyxel.KEY_L) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y + spacing * 2, text_len)):
                self._model.state = GameState.LEADERBOARD
            elif pyxel.btnp(pyxel.KEY_E) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y + spacing * 3, text_len)):
                quit()

        elif self._model.state == GameState.LEADERBOARD:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                min_y = pyxel.height // 2 - 100
                max_y = pyxel.height // 2 + 100
                if self._is_clicked_button(pyxel.width // 2 + 45, min_y + 4, height=14):
                    self.leaderboard_state = (self.leaderboard_state + 1) % 2
                    self.leaderboard_page = 1
                    self.update_leaderboard()
                elif self._is_clicked_button(pyxel.width // 2, max_y - 12, height=14):
                    self.leaderboard_page = min(self.leaderboard_page + 1, self.leaderboard_max_page)
                elif self._is_clicked_button(pyxel.width // 2 - 16, max_y - 12, height=14):
                    self.leaderboard_page = max(1, self.leaderboard_page - 1)
                elif self._is_clicked_text(21, 6, 4):
                    self._model.state = self.previous_state

        
        elif self._model.state == GameState.GAME:
            if self._model.start_round:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._model.mode is None:
                    start_y = pyxel.height // 2 - 55 + 70
                    spacing = 17
                    start_1x = pyxel.width // 2 - 8 - 32
                    start_2x = pyxel.width // 2 + 8 + 32
                    if self._is_clicked_text(21, 6, 4):
                        self._model.state = self.previous_state
                    elif self._is_clicked_text(start_1x, start_y, 8):
                        self._model.mode = Mode.CAMPAIGN_NORMAL
                    elif self._is_clicked_text(start_1x, start_y + spacing, 8):
                        self._model.mode = Mode.CAMPAIGN_HARD
                    if self._is_clicked_text(start_2x, start_y, 8):
                        self._model.mode = Mode.ENDLESS_NORMAL
                    elif self._is_clicked_text(start_2x, start_y + spacing, 8):
                        self._model.mode = Mode.ENDLESS_HARD

                if self._model.mode:
                    self.take_input()
            elif self.place_tower:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.check_tower()
                elif pyxel.btnp(pyxel.KEY_RETURN):
                    self.place_tower = False
                else:
                    pass
            elif self.select_tower:
                if self.orientation:
                    self.edit_orientation()
                elif self.upgrade:
                    self.upgrade_tower()
                elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.click_tower_info()
            else:
                if pyxel.btnp(pyxel.KEY_S):
                    self.previous_state = GameState.GAME
                    self._model.state = GameState.SETTINGS
                else:
                    angle = math.degrees(math.atan2(
                        pyxel.mouse_y - pyxel.height // 2,
                        pyxel.mouse_x - pyxel.height // 2
                    ))
                    self._model.shooter.edit_orientation(angle)
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                        self._model.shooter.shoot_bullet(angle)
                    elif pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                        for tower in self._model.towers:
                            if self._is_clicked_button(tower.x, tower.y):
                                self.select_tower = tower
                                self.tx, self.ty = tower.x, tower.y
                                break

                    self._model.update()
        elif self._model.state == GameState.SETTINGS:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                start_y = pyxel.height // 2 - 90 - 3
                start_1x = pyxel.width // 2 - 100 + 5
                end_1x = pyxel.width // 2 - 19
                start_2x = end_1x + 16 + 4
                end_2x = pyxel.width // 2 + 100 - 5 - 16
                spacing = 17
                
                if self._is_clicked_button(start_1x, start_y + spacing * 2):
                    self._model.set_config("smooth", 1)
                elif self._is_clicked_button(start_1x, start_y + spacing * 3):
                    self._model.set_config("limit", self._model.limit - 1)
                    self._model.save_settings()
                elif self._is_clicked_button(end_1x, start_y + spacing * 3):
                    self._model.set_config("limit", self._model.limit + 1)
                    self._model.save_settings()
                elif self._is_clicked_button(start_1x, start_y + spacing * 5):
                    self._model.set_config("shooter_rate", self._model.shooter_rate - 0.1)
                elif self._is_clicked_button(end_1x, start_y + spacing * 5):
                    self._model.set_config("shooter_rate", self._model.shooter_rate + 0.1)
                elif self._is_clicked_button(start_1x, start_y + spacing * 6):
                    self._model.set_config("shooter_speed", self._model.shooter_speed - 0.1)
                elif self._is_clicked_button(end_1x, start_y + spacing * 6):
                    self._model.set_config("shooter_speed", self._model.shooter_speed + 0.1)
                elif self._is_clicked_button(start_1x, start_y + spacing * 8):
                    self._model.set_config("tower_rate", self._model.tower_rate - 0.1)
                elif self._is_clicked_button(end_1x, start_y + spacing * 8):
                    self._model.set_config("tower_rate", self._model.tower_rate + 0.1)
                elif self._is_clicked_button(start_1x, start_y + spacing * 9):
                    self._model.set_config("tower_speed", self._model.tower_speed - 0.1)
                elif self._is_clicked_button(end_1x, start_y + spacing * 9):
                    self._model.set_config("tower_speed", self._model.tower_speed + 0.1)
                elif self._is_clicked_button(start_2x, start_y + spacing * 2):
                    self._model.set_config("enemy_speed", self._model.enemy_speed - 0.1)
                elif self._is_clicked_button(end_2x, start_y + spacing * 2):
                    self._model.set_config("enemy_speed", self._model.enemy_speed + 0.1)
                
                elif self._is_clicked_button(start_2x, start_y + spacing * 3):
                    self._model.regen_h = max(5, self._model.regen_h - 1)
                    for enemy in self._model.enemies:
                        if isinstance(enemy, Regenerator):
                            enemy.h = self._model.regen_h
                    self._model.save_settings()
                
                elif self._is_clicked_button(end_2x, start_y + spacing * 3):
                    self._model.regen_h += 1
                    for enemy in self._model.enemies:
                        if isinstance(enemy, Regenerator):
                            enemy.h = self._model.regen_h
                    self._model.save_settings()
                    
                elif self._is_clicked_button(start_2x, start_y + spacing * 4):
                    self._model.cham_freq = max(3.0, self._model.cham_freq - 0.1)
                    for enemy in self._model.enemies:
                        if isinstance(enemy, Chameleon):
                            enemy.freq = 1 / (self._model.cham_freq * 30)
                    self._model.save_settings()
                    
                elif self._is_clicked_button(end_2x, start_y + spacing * 4):
                    self._model.cham_freq += 0.1
                    for enemy in self._model.enemies:
                        if isinstance(enemy, Chameleon):
                            enemy.freq = 1 / (self._model.cham_freq * 30)
                    self._model.save_settings()
                    
                elif self._is_clicked_button(start_2x, start_y + spacing * 6):
                    self._model.set_config("lives", self._model.lives - 1)
                elif self._is_clicked_button(end_2x, start_y + spacing * 6):
                    self._model.set_config("lives", self._model.lives + 1)
                elif self._is_clicked_text(pyxel.width // 2, start_y + spacing * 10, len("  EXIT  ")):
                    self._model.save_settings()
                    self._model.state = self.previous_state
        
        elif self._model.state == GameState.NAME_INPUT:
            self.take_name_input()
        
        elif self._model.state == GameState.GAME_OVER:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if self._is_clicked_text(pyxel.width // 2, pyxel.height // 2 + 1, 20):
                    self._model.restart_game()

                elif self._is_clicked_text(pyxel.width // 2, pyxel.height // 2 + 17, 20):
                    pyxel.quit()
                    



    def draw(self):
        if self._model.hit_enemy:
            self._model.hit_enemy = False
            pyxel.playm(0, 0, loop=False)
        
        self._view.reset_screen()
        self._view.draw_grid()
        
        if self._model.state == GameState.START:
            self._view.draw_start(self.enemy_start)
        
        elif self._model.state == GameState.GAME:
            if self._model.start_round:
                if self._model.mode is None:
                    self._view.draw_modes()
                else:
                    self._view.draw_inputs(self.input, self._model.exp >= 5)
                    if self._model.mode in (Mode.CAMPAIGN_HARD, Mode.CAMPAIGN_NORMAL):
                        self._view.draw_round(self._model.rounds)
            else:
                self._view.draw_next_color(self._model.shooter.next_color)
                self._view.draw_exp(self._model.exp)
                self._view.draw_lives(self._model.lives)
                self._view.draw_routes(self._model.routes)
                self._view.draw_tower_bullets(self._model.towers)
                self._view.draw_enemies(self._model.enemies)
                self._view.draw_tunnels(self._model.tunnels)
                self._view.draw_towers(self._model.towers)
                self._view.draw_bullets(self._model.shooter.bullets)
                self._view.draw_shooter(self._model.shooter)

                if self.place_tower:
                    self._view.draw_exit_placement()

                    if self._model.exp >= 5:
                        self._view.draw_tower_placement(pyxel.mouse_x, pyxel.mouse_y, (self._model.blocked_cells | self._model.tower_cells))
                elif self.select_tower:
                    self._view.draw_tower_info(self.select_tower)

                    if self.orientation:
                        self._view.draw_orientation()
        
        elif self._model.state == GameState.SETTINGS:
            self._view.draw_settings(self._model.smooth, self._model.limit, self._model.shooter_rate, self._model.shooter_speed, self._model.tower_rate, self._model.tower_speed, self._model.regen_h, self._model.cham_freq, self._model.enemy_speed, self._model.lives)

        elif self._model.state == GameState.LEADERBOARD:
            self._view.draw_leaderboard(self.leaderboard_state, self.leaderboard_page, self.leaderboard_normal, self.leaderboard_hard)
        
        elif self._model.state == GameState.NAME_INPUT:
            self._view.draw_name_input(self.name_input)
        
        elif self._model.state == GameState.GAME_OVER:
            self._view.draw_game_over(self._model.rounds_survived)
