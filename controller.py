from model.model import Model
from model.enemy import Regenerator, Chameleon
from model.tower import Tower
from view import View
from utils import Orientation, GameState, Mode

import pyxel
import math
import json

class Controller:
    def __init__(self, model: Model, view: View):
        self._model: Model = model
        self._view: View = view

        self.input: str = ""
        self.place_tower: bool = False
        self.select_tower: Tower = None
        self.orientation: bool = False
        self.upgrade: bool = False
        self.tx: int = 0
        self.ty: int = 0
        self.previous_state: GameState = None

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

    def update(self):
        if not self._model.is_game_over:
            if self._model.state == GameState.START:
                max_y = pyxel.height // 2 - 51 + 60
                spacing = 16
                text_len = 12
                if pyxel.btnp(pyxel.KEY_P) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y, text_len)):
                    self._model.state = GameState.GAME
                elif pyxel.btnp(pyxel.KEY_S) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y + spacing, text_len)):
                    self.previous_state = GameState.START
                    self._model.state = GameState.SETTINGS
                elif pyxel.btnp(pyxel.KEY_I) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y + spacing * 2, text_len)):
                    self._model.state = GameState.INFO
                elif pyxel.btnp(pyxel.KEY_E) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_clicked_text(pyxel.width // 2, max_y + spacing * 3, text_len)):
                    quit()
            elif self._model.state == GameState.GAME:
                if self._model.start_round:
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._model.mode is None:
                        start_y = pyxel.height // 2 - 55 + 70
                        spacing = 17
                        start_1x = pyxel.width // 2 - 8 - 32
                        start_2x = pyxel.width // 2 + 8 + 32
                        if self._is_clicked_text(start_1x, start_y, 8):
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
                        self._model.smooth = not self._model.smooth
                    elif self._is_clicked_button(start_1x, start_y + spacing * 3):
                        with open('settings.json', 'r+') as f:
                            data = json.load(f)
                            self._model.limit = max(5, self._model.limit - 1)
                            data['n_enemies'] = self._model.limit
                            f.seek(0)
                            json.dump(data, f)
                            f.truncate()
                    elif self._is_clicked_button(end_1x, start_y + spacing * 3):
                        with open('settings.json', 'r+') as f:
                            data = json.load(f)
                            self._model.limit += 1
                            data['n_enemies'] = self._model.limit
                            f.seek(0)
                            json.dump(data, f)
                            f.truncate()
                    elif self._is_clicked_button(start_1x, start_y + spacing * 5):
                        self._model.shooter_rate = max(0.9, self._model.shooter_rate - 0.1)
                        self._model.shooter.rate = self._model.shooter_rate / 30
                    elif self._is_clicked_button(end_1x, start_y + spacing * 5):
                        self._model.shooter_rate += 0.1
                        self._model.shooter.rate = self._model.shooter_rate / 30
                    elif self._is_clicked_button(start_1x, start_y + spacing * 6):
                        self._model.shooter_speed = max(1.0, self._model.shooter_speed - 0.1)
                        self._model.shooter.speed = pyxel.height / (self._model.shooter_speed * 30)
                        for bullet in self._model.shooter.bullets:
                            bullet.speed = self._model.shooter.speed
                    elif self._is_clicked_button(end_1x, start_y + spacing * 6):
                        self._model.shooter_speed += 0.1
                        self._model.shooter.speed = pyxel.height / (self._model.shooter_speed * 30)
                        for bullet in self._model.shooter.bullets:
                            bullet.speed = self._model.shooter.speed
                    elif self._is_clicked_button(start_1x, start_y + spacing * 8):
                        self._model.tower_rate = max(0.5, self._model.tower_rate - 0.1)
                        for tower in self._model.towers:
                            tower.rate = self._model.tower_rate / 30
                    elif self._is_clicked_button(end_1x, start_y + spacing * 8):
                        self._model.tower_rate += 0.1
                        for tower in self._model.towers:
                            tower.rate = self._model.tower_rate / 30
                    elif self._is_clicked_button(start_1x, start_y + spacing * 9):
                        self._model.tower_speed = max(1.0, self._model.tower_speed - 0.1)
                        for tower in self._model.towers:
                            tower.speed = pyxel.height / (self._model.tower_speed * 30)
                            for bullet in tower.bullets:
                                bullet.speed = tower.speed
                    elif self._is_clicked_button(end_1x, start_y + spacing * 9):
                        self._model.tower_speed += 0.1
                        for tower in self._model.towers:
                            tower.speed = pyxel.height / (self._model.tower_speed * 30)
                            for bullet in tower.bullets:
                                bullet.speed = tower.speed
                    elif self._is_clicked_button(start_2x, start_y + spacing * 2):
                        self._model.enemy_speed = max(0.1, self._model.enemy_speed - 0.1)
                        self._model.timer = 1
                        self._model.spawn_interval = 1 / (self._model.enemy_speed * 30)
                        for enemy in self._model.enemies:
                            enemy.speed = self._model.spawn_interval
                            enemy.timer = 1
                    elif self._is_clicked_button(end_2x, start_y + spacing * 2):
                        self._model.enemy_speed += 0.1
                        self._model.timer = 1
                        self._model.spawn_interval = 1 / (self._model.enemy_speed * 30)
                        for enemy in self._model.enemies:
                            enemy.speed = self._model.spawn_interval
                            enemy.timer = 1
                    elif self._is_clicked_button(start_2x, start_y + spacing * 3):
                        self._model.regen_h = max(5, self._model.regen_h - 1)
                        for enemy in self._model.enemies:
                            if isinstance(enemy, Regenerator):
                                enemy.h = self._model.regen_h
                    elif self._is_clicked_button(end_2x, start_y + spacing * 3):
                        self._model.regen_h += 1
                        for enemy in self._model.enemies:
                            if isinstance(enemy, Regenerator):
                                enemy.h = self._model.regen_h
                    elif self._is_clicked_button(start_2x, start_y + spacing * 4):
                        self._model.cham_freq = max(3.0, self._model.cham_freq - 0.1)
                        for enemy in self._model.enemies:
                            if isinstance(enemy, Chameleon):
                                enemy.freq = 1 / (self._model.cham_freq * 30)
                    elif self._is_clicked_button(end_2x, start_y + spacing * 4):
                        self._model.cham_freq += 0.1
                        for enemy in self._model.enemies:
                            if isinstance(enemy, Chameleon):
                                enemy.freq = 1 / (self._model.cham_freq * 30)
                    elif self._is_clicked_button(start_2x, start_y + spacing * 6):
                        with open('settings.json', 'r+') as f:
                            data = json.load(f)
                            self._model.lives = max(2, self._model.lives - 1)
                            data['n_lives'] = self._model.lives
                            f.seek(0)
                            json.dump(data, f)
                            f.truncate()
                    elif self._is_clicked_button(end_2x, start_y + spacing * 6):
                        with open('settings.json', 'r+') as f:
                            data = json.load(f)
                            self._model.lives += 1
                            data['n_lives'] = self._model.lives
                            f.seek(0)
                            json.dump(data, f)
                            f.truncate()
                    elif self._is_clicked_text(pyxel.width // 2, start_y + spacing * 10, len("  EXIT  ")):
                        self._model.state = self.previous_state



    def draw(self):
        if self._model.hit_enemy:
            self._model.hit_enemy = False
            pyxel.playm(0, 0, loop=False)
        self._view.reset_screen()
        if not self._model.is_game_over:
            self._view.draw_grid()
            if self._model.state == GameState.START:
                self._view.draw_start(self._model.grid)
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
        else:
            self._view.draw_game_over()
