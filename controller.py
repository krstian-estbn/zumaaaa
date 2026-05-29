from model1 import Model, Enemy
from view1 import View
from utils import Orientation

import pyxel
import math

class Controller:
    def __init__(self, model: Model, view: View):
        self._model = model
        self._view = view

        # self.grid = [(col, row) for row in range(0, pyxel.height, 16) for col in range(0, pyxel.width, 16)]
        self.input = ""
        self.place_tower = None
        self.select_tower = None
        self.orientation = None
        self.upgrade = None
        self.tx = 0
        self.ty = 0

    def start_game(self):
        pyxel.load("bgm.pyxres")
        pyxel.playm(0, 0, loop=True)

        pyxel.load("zuma.pyxres")
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
                self.orientation = None
                break
            else:
                pass

    def upgrade_tower(self):
        assert self.select_tower

        if self._model.exp >= 5:
            self.select_tower.upgrade()
            self._model.exp -= 5
        self.upgrade = None

    def click_tower_info(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if 110 <= mx <= 110 + 16 and pyxel.height - 30 <= my <= pyxel.height - 30 + 16:
            self.orientation = True
        elif 10 <= mx <= 10 + 16 and pyxel.height - 30 <= my <= pyxel.height - 30 + 16:
            self.upgrade = True
        elif pyxel.width - 10 - 4 <= mx <= pyxel.width - 10 and pyxel.height - 40 <= my <= pyxel.height - 40 + 6:
            self.select_tower = None
        else:
            pass

    def update(self):
        if not self._model.is_game_over:
            if self._model.start_round:
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
                angle = math.degrees(math.atan2(
                    pyxel.mouse_y - pyxel.height // 2,
                    pyxel.mouse_x - pyxel.height // 2
                ))
                self._model.shooter.edit_orientation(angle)
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self._model.shooter.shoot_bullet(angle)
                elif pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                    for tower in self._model.towers:
                        if tower.x <= pyxel.mouse_x < tower.x + 16 and tower.y <= pyxel.mouse_y < tower.y + 16:
                            self.select_tower = tower
                            self.tx, self.ty = tower.x, tower.y
                            break

                self._model.update()


    def draw(self):
        self._view.reset_screen()
        if not self._model.is_game_over:
            if self._model.start_round:
                self._view.draw_inputs(self.input, self._model.exp >= 5)
                self._view.draw_round(self._model.rounds)
            else:
                self._view.draw_grid()
                self._view.draw_next_color(self._model.shooter.next_color)
                self._view.draw_exp(self._model.exp)
                self._view.draw_lives(self._model.lives)
                self._view.draw_routes(self._model.routes)
                self._view.draw_shooter(self._model.shooter)
                self._view.draw_bullets(self._model.shooter.bullets)
                self._view.draw_tower_bullets(self._model.towers)
                self._view.draw_enemies(self._model.enemies)
                self._view.draw_tunnels(self._model.tunnels)
                self._view.draw_towers(self._model.towers)

                if self.place_tower:
                    self._view.draw_exit_placement()

                    if self._model.exp >= 5:
                        self._view.draw_tower_placement(pyxel.mouse_x, pyxel.mouse_y, (self._model.blocked_cells | self._model.tower_cells))
                elif self.select_tower:
                    self._view.draw_tower_info(self.select_tower)

                    if self.orientation:
                        self._view.draw_orientation()
        else:
            self._view.draw_game_over()
