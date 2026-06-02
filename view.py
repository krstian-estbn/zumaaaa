import pyxel
import math
import json

from random import Random
from utils import Color, Orientation, Mode
from model.enemy import Enemy, Regenerator, Chameleon

BlOCK_SIZE = 13
PADDING = 3

def create_text(text, x, y, bg_color, text_color, center=True):
    text_width = 4 * len(text)
    text_height = 6

    text_x = x - text_width // 2 if center else x
    text_y = y + PADDING + 2

    rect_x = text_x - PADDING
    rect_y = text_y - PADDING
    rect_width = text_width + (PADDING * 2)
    rect_height = text_height + (PADDING * 2)

    pyxel.rect(rect_x - 1, rect_y - 1, rect_width + 2, rect_height + 2, text_color)
    pyxel.rect(rect_x, rect_y, rect_width, rect_height, bg_color)
    pyxel.text(text_x, text_y, text, text_color)

def create_button(x, y, u):
    pyxel.blt(x, y, 0, u, 128, 16, 16, 0)

def create_configurable(text, x1, x2, y, bg_color, text_color):
    create_button(x1, y, 48)
    create_text(text, x1 + 16 + 8, y, bg_color, text_color, False)
    create_button(x2, y, 32)

class View:
    def draw_shooter(self, shooter):
        if shooter.color == Color.YELLOW:
            pyxel.blt(pyxel.width // 2 - 8, pyxel.height // 2 - 8, 0, 16, 16, 16, 16, 0, shooter.angle)
        elif shooter.color == Color.GREEN:
            pyxel.blt(pyxel.width // 2 - 8, pyxel.height // 2 - 8, 0, 32, 16, 16, 16, 0, shooter.angle)
        elif shooter.color == Color.BLUE:
            pyxel.blt(pyxel.width // 2 - 8, pyxel.height // 2 - 8, 0, 48, 16, 16, 16, 0, shooter.angle)
        elif shooter.color == Color.PINK:
            pyxel.blt(pyxel.width // 2 - 8, pyxel.height // 2 - 8, 0, 0, 32, 16, 16, 0, shooter.angle)
        else:
            pyxel.blt(pyxel.width // 2 - 8, pyxel.height // 2 - 8, 0, 16, 32, 16, 16, 0, shooter.angle)
            

    def draw_enemies(self, enemies):
        for enemy in enemies:
            if not enemy.spawned:
                if isinstance(enemy, Regenerator):
                    if enemy.color == Color.YELLOW:
                        pyxel.blt(enemy.x, enemy.y, 0, 0, 144, 16, 16, 0)
                    elif enemy.color == Color.GREEN:
                        pyxel.blt(enemy.x, enemy.y, 0, 16, 144, 16, 16, 0)
                    elif enemy.color == Color.BLUE:
                        pyxel.blt(enemy.x, enemy.y, 0, 32, 144, 16, 16, 0)
                    elif enemy.color == Color.PINK:
                        pyxel.blt(enemy.x, enemy.y, 0, 48, 144, 16, 16, 0)
                    else:
                        pyxel.blt(enemy.x, enemy.y, 0, 0, 160, 16, 16, 0)
                elif isinstance(enemy, Chameleon):
                    if enemy.color == Color.YELLOW:
                        pyxel.blt(enemy.x, enemy.y, 0, 0, 176, 16, 16, 0)
                    elif enemy.color == Color.GREEN:
                        pyxel.blt(enemy.x, enemy.y, 0, 16, 176, 16, 16, 0)
                    elif enemy.color == Color.BLUE:
                        pyxel.blt(enemy.x, enemy.y, 0, 32, 176, 16, 16, 0)
                    elif enemy.color == Color.PINK:
                        pyxel.blt(enemy.x, enemy.y, 0, 48, 176, 16, 16, 0)
                    else:
                        pyxel.blt(enemy.x, enemy.y, 0, 0, 192, 16, 16, 0)
                else:
                    if enemy.color == Color.YELLOW:
                        pyxel.blt(enemy.x, enemy.y, 0, 0, 0, 16, 16, 0)
                    elif enemy.color == Color.GREEN:
                        pyxel.blt(enemy.x, enemy.y, 0, 16, 0, 16, 16, 0)
                    elif enemy.color == Color.BLUE:
                        pyxel.blt(enemy.x, enemy.y, 0, 32, 0, 16, 16, 0)
                    elif enemy.color == Color.PINK:
                        pyxel.blt(enemy.x, enemy.y, 0, 48, 0, 16, 16, 0)
                    else:
                        pyxel.blt(enemy.x, enemy.y, 0, 0, 16, 16, 16, 0)


    def draw_bullets(self, bullets):
        for bullet in bullets:
            if bullet.color == Color.YELLOW:
                pyxel.blt(bullet.x, bullet.y, 0, 32, 32, 8, 8, 0)
            elif bullet.color == Color.GREEN:
                pyxel.blt(bullet.x, bullet.y, 0, 40, 32, 8, 8, 0)
            elif bullet.color == Color.BLUE:
                pyxel.blt(bullet.x, bullet.y, 0, 32, 40, 8, 8, 0)
            elif bullet.color == Color.PINK:
                pyxel.blt(bullet.x, bullet.y, 0, 40, 40, 8, 8, 0)
            else:
                pyxel.blt(bullet.x, bullet.y, 0, 48, 32, 8, 8, 0)

    def draw_tower_bullets(self, towers):
        for tower in towers:
            for bullet in tower.bullets:
                if bullet.color == Color.YELLOW:
                    yellow = {Orientation.UP: (48, 80), Orientation.DOWN: (56, 80), Orientation.RIGHT: (48, 88), Orientation.LEFT: (56, 88)}
                    pyxel.blt(bullet.x, bullet.y, 0, *yellow[bullet.orientation], 8, 8, 0)
                elif bullet.color == Color.GREEN:
                    green = {Orientation.UP: (0, 96), Orientation.DOWN: (8, 96), Orientation.RIGHT: (0, 104), Orientation.LEFT: (8, 104)}
                    pyxel.blt(bullet.x, bullet.y, 0, *green[bullet.orientation], 8, 8, 0)
                elif bullet.color == Color.BLUE:
                    blue = {Orientation.UP: (16, 96), Orientation.DOWN: (24, 96), Orientation.RIGHT: (16, 104), Orientation.LEFT: (24, 104)}
                    pyxel.blt(bullet.x, bullet.y, 0, *blue[bullet.orientation], 8, 8, 0)
                elif bullet.color == Color.PINK:
                    pink = {Orientation.UP: (32, 96), Orientation.DOWN: (40, 96), Orientation.RIGHT: (32, 104), Orientation.LEFT: (40, 104)}
                    pyxel.blt(bullet.x, bullet.y, 0, *pink[bullet.orientation], 8, 8, 0)
                else:
                    white = {Orientation.UP: (48, 96), Orientation.DOWN: (56, 96), Orientation.RIGHT: (48, 104), Orientation.LEFT: (56, 104)}
                    pyxel.blt(bullet.x, bullet.y, 0, *white[bullet.orientation], 8, 8, 0)


    def reset_screen(self):
        pyxel.cls(0)

    def draw_grid(self, cell_size: int = 16) -> None:
        for x in range(cell_size, pyxel.width, cell_size):
            pyxel.line(x, 0, x, pyxel.height, 1)

        for y in range(cell_size, pyxel.height, cell_size):
            pyxel.line(0, y, pyxel.width, y, 1)

    def draw_round(self, rounds):
        pyxel.text(pyxel.width // 2 - (4 * len(f"ROUNDS LEFT: {rounds}")) // 2, pyxel.height // 2, f"ROUNDS LEFT: {rounds}", pyxel.COLOR_WHITE)

    def draw_routes(self, routes):
        for k, route in enumerate(routes):
            v = 48 if k == 0 else 64
            for i in range(len(route) - 1):
                if route[i]['direction'] == route[i+1]['direction']:
                    if route[i]['direction'] == 1:
                        pyxel.blt(route[i]['x'], route[i]['y'], 0, 0, v, 16, 16, 0)
                    else:
                        pyxel.blt(route[i]['x'], route[i]['y'], 0, 32, v, 16, 16, 0)
                else:
                    if route[i]['direction'] == 1:
                        pyxel.blt(route[i]['x'], route[i]['y'], 0, 16, v, 16, 16, 0)
                    else:
                        pyxel.blt(route[i]['x'], route[i]['y'], 0, 48, v, 16, 16, 0)
            pyxel.blt(route[-1]['x'], route[-1]['y'], 0, 0, v, 16, 16, 0)

    def draw_tunnels(self, tunnels):
        for tunnel in tunnels:
            for i in range(len(tunnel)):
                pyxel.blt(tunnel[i]["x"], tunnel[i]["y"], 0, 64, 0, 16, 16, 0)

    def draw_exp(self, exp):
        pyxel.text(10, 10, f"EXP: {exp}", pyxel.COLOR_WHITE)

    def draw_lives(self, lives):
        pyxel.text(pyxel.width - 10 - (4 * len(f"LIVES: {lives}")), 10, f"LIVES: {lives}", pyxel.COLOR_WHITE)

    def draw_next_color(self, next_color):
        colors = {Color.YELLOW: pyxel.COLOR_YELLOW, Color.GREEN: pyxel.COLOR_GREEN, Color.BLUE: pyxel.COLOR_LIGHT_BLUE, Color.PINK: pyxel.COLOR_PINK, Color.WHITE: pyxel.COLOR_WHITE}
        pyxel.text(pyxel.width - 10 - 6 - 4 * len("NEXT COLOR: "), pyxel.height - 10 - 5, "NEXT COLOR: ", pyxel.COLOR_WHITE)
        pyxel.circb(pyxel.width - 10 - 3, pyxel.height - 10 - 3, 3, pyxel.COLOR_NAVY)
        pyxel.circ(pyxel.width - 10 - 3, pyxel.height - 10 - 3, 2, colors[next_color])

    def draw_game_over(self, rounds_survived: int):
        center_x = pyxel.width // 2
        center_y = pyxel.height // 2
        width = 140
        height = 90
        x = center_x - width // 2
        y = center_y - height // 2

        
        pyxel.rect(x + 3, y + 3, width, height, pyxel.COLOR_BLACK)       
        pyxel.rect(x, y, width, height, pyxel.COLOR_NAVY)
        pyxel.rect(x + 4, y + 4, width - 8, height - 8, pyxel.COLOR_DARK_BLUE)


        pyxel.text(center_x - (4 * len("GAME OVER")) // 2, y + 14, "GAME OVER", pyxel.COLOR_RED)
        survived = f"ROUNDS: {rounds_survived}"
        pyxel.text(center_x - (4 * len(survived)) // 2, y + 30, survived, pyxel.COLOR_WHITE)

        create_text("  PLAY AGAIN  ", center_x, y + 46, pyxel.COLOR_LIME, pyxel.COLOR_GREEN)
        create_text("  EXIT  ", center_x, y + 62, pyxel.COLOR_PINK, pyxel.COLOR_RED)

    def draw_tower_placement(self, mx, my, blocked_cells):
        tx = (mx // 16) * 16
        ty = (my // 16) * 16

        blocked = False

        for x, y in blocked_cells:
            if not (tx <= x < tx + 16 and ty <= y < ty + 16) and not (tx <= pyxel.width // 2 < tx + 16 and ty <= pyxel.height // 2 < ty + 16):
                continue
            else:
                blocked = True
                break

        if blocked:
            pyxel.blt(tx, ty, 0, 16, 80, 16, 16, 0)
        else:
            pyxel.blt(tx, ty, 0, 0, 80, 16, 16, 0)

    def draw_tower_info(self, tower):
        pyxel.rect(0, pyxel.height - 50, pyxel.width, 50, pyxel.COLOR_NAVY)
        pyxel.rectb(0, pyxel.height - 50, pyxel.width, 50, pyxel.COLOR_DARK_BLUE)
        pyxel.text(10, pyxel.height - 40, f"EDIT TOWER: Level {tower.level}", pyxel.COLOR_WHITE)
        pyxel.blt(10, pyxel.height - 30, 0, 0, 112, 16, 16, 0)
        pyxel.text(30, pyxel.height - 30 + 5, "UPGRADE [5 EXP]", pyxel.COLOR_WHITE)
        pyxel.blt(110, pyxel.height - 30, 0, 16, 112, 16, 16, 0)
        pyxel.text(130, pyxel.height - 30 + 5, "EDIT DIRECTION", pyxel.COLOR_WHITE)
        pyxel.text(pyxel.width - 10 - 4, pyxel.height - 40, "X", pyxel.COLOR_WHITE)

    def draw_inputs(self, inp, can_place_tower):
        yn = "[Y/N]" if can_place_tower else "[N]"
        pyxel.text(10, pyxel.height - 20, f"PLACE TOWER {yn}? {inp}_", pyxel.COLOR_WHITE)

    def draw_towers(self, towers):
        for tower in towers:
            if tower.level == 1:
                pyxel.blt(tower.x, tower.y, 0, 32, 80, 16, 16, 0)
            elif tower.level == 2:
                pyxel.blt(tower.x, tower.y, 0, 32, 112, 16, 16, 0)

    def draw_orientation(self):
        text = "Choose orientation [W/A/S/D]."
        pyxel.rect(pyxel.width // 2 - (4 * len(text)) // 2 - 4, pyxel.height // 2 - 2, (4 * len(text)) + 4, 10, pyxel.COLOR_NAVY)
        pyxel.text(pyxel.width // 2 - (4 * len(text)) // 2, pyxel.height // 2, text, pyxel.COLOR_WHITE)

    def draw_exit_placement(self):
        text = "Press [Enter] to continue."
        pyxel.rect(10, pyxel.height - 22, (4 * len(text)) + 4, 10, pyxel.COLOR_NAVY)
        pyxel.text(14, pyxel.height - 20, text, pyxel.COLOR_WHITE)

    def draw_start(self, enemies):
        for x, y, u, v in enemies:
            pyxel.blt(x, y, 0, u, v, 16, 16, 0)

        TOTAL_HEIGHT = 102
        min_y = pyxel.height // 2 - 50
        max_y = pyxel.height // 2 - 51 + 60
        
        pyxel.blt(pyxel.width // 2 - 64, min_y, 1, 0, 0, 128, 32, 0)
        pyxel.blt(pyxel.width // 2 - 64, min_y + 32 + 4, 1, 0, 96, 128, 16, 0)
        create_text("PLAY".center(14), pyxel.width // 2, max_y, pyxel.COLOR_PEACH, pyxel.COLOR_BROWN)
        create_text("SETTINGS".center(14), pyxel.width // 2, max_y + (BlOCK_SIZE + PADDING), pyxel.COLOR_YELLOW, pyxel.COLOR_ORANGE)
        create_text(" LEADERBOARD".center(14), pyxel.width // 2, max_y + (BlOCK_SIZE + PADDING) * 2, pyxel.COLOR_LIME, pyxel.COLOR_GREEN)
        create_text("EXIT".center(14), pyxel.width // 2, max_y + (BlOCK_SIZE + PADDING) * 3, pyxel.COLOR_PINK, pyxel.COLOR_RED)

        
    def draw_settings(self, check_smooth, enemies, shooter_rate, shooter_speed, tower_rate, tower_speed, regen, chameleon, enemy_speed, lives):
        min_x = pyxel.width // 2 - 100
        min_y = pyxel.height // 2 - 90
        max_y = pyxel.height // 2 + 90
        spacing = BlOCK_SIZE + PADDING + 1
        pyxel.rect(min_x - 1, min_y - 1, 202, 182, pyxel.COLOR_NAVY)
        pyxel.rect(min_x, min_y, 200, 180, pyxel.COLOR_DARK_BLUE)
        
        start_y = min_y - 3
        start_1x = min_x + 5
        end_1x = pyxel.width // 2 - 19
        start_2x = end_1x + 16 + 4
        end_2x = pyxel.width // 2 + 100 - 5 - 16
        center_1x = pyxel.width // 2 - 47
        center_2x = pyxel.width // 2 + 47

        create_text("  SETTINGS  ", pyxel.width // 2, start_y, pyxel.COLOR_PINK, pyxel.COLOR_RED)
        create_text("ENEMIES", pyxel.width // 2, start_y + spacing, pyxel.COLOR_WHITE, pyxel.COLOR_NAVY)
        if not check_smooth:
            create_button(start_1x, start_y + spacing * 2, 0)
        else:
            create_button(start_1x, start_y + spacing * 2, 16)
        create_text("SMOOTHNESS".ljust(11), start_1x + 16 + 8, start_y + spacing * 2, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY, False)
        create_configurable(f"NUMBER: {enemies}".ljust(11), start_1x, end_1x, start_y + spacing * 3, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)
        create_configurable(f"SPEED: {enemy_speed:.1f}".ljust(11), start_2x, end_2x, start_y + spacing * 2, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)
        create_configurable(f"REGEN: {regen}".ljust(11), start_2x, end_2x, start_y + spacing * 3, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)
        create_configurable(f"CHAM: {chameleon:.1f}".ljust(11), start_2x, end_2x, start_y + spacing * 4, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)


        create_text("SHOOTER", center_1x, start_y + spacing * 4, pyxel.COLOR_WHITE, pyxel.COLOR_NAVY)
        create_configurable(f"RATE: {shooter_rate:.1f}".ljust(11), start_1x, end_1x, start_y + spacing * 5, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)
        create_configurable(f"SPEED: {shooter_speed:.1f}".ljust(11), start_1x, end_1x, start_y + spacing * 6, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)

        create_text("PLAYER", center_2x, start_y + spacing * 5, pyxel.COLOR_WHITE, pyxel.COLOR_NAVY)
        create_configurable(f"LIVES: {lives}".ljust(11), start_2x, end_2x, start_y + spacing * 6, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)

        create_text("TOWER", center_1x, start_y + spacing * 7, pyxel.COLOR_WHITE, pyxel.COLOR_NAVY)
        create_configurable(f"RATE: {tower_rate:.1f}".ljust(11), start_1x, end_1x, start_y + spacing * 8, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)
        create_configurable(f"SPEED: {tower_speed:.1f}".ljust(11), start_1x, end_1x, start_y + spacing * 9, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)

        create_text("  EXIT  ", pyxel.width // 2, start_y + spacing * 10, pyxel.COLOR_PINK, pyxel.COLOR_RED)

    def draw_modes(self):
        create_text("EXIT", 21, 6, pyxel.COLOR_PINK, pyxel.COLOR_RED)
        min_y = pyxel.height // 2 - 55
        pyxel.blt(pyxel.width // 2 - 64 - 8, min_y, 1, 64, 32, 64, 64, 0)
        pyxel.blt(pyxel.width // 2 + 8, min_y, 1, 0, 32, 64, 64, 0)
        create_text(" NORMAL ", pyxel.width // 2 - 8 - 32, min_y + 70, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)
        create_text("  HARD  ", pyxel.width // 2 - 8 - 32, min_y + 70 + BlOCK_SIZE + PADDING, pyxel.COLOR_PINK, pyxel.COLOR_RED)
        create_text(" NORMAL ", pyxel.width // 2 + 8 + 32, min_y + 70, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)
        create_text("  HARD  ", pyxel.width // 2 + 8 + 32, min_y + 70 + BlOCK_SIZE + PADDING, pyxel.COLOR_PINK, pyxel.COLOR_RED)
    
    def draw_name_input(self, name: str):
        # outer border
        outer_width = 190
        outer_height = 70
        outer_x = pyxel.width // 2 - outer_width // 2
        outer_y = pyxel.height // 2 - outer_height // 2

        pyxel.rect(outer_x + 3, outer_y + 3, outer_width, outer_height, pyxel.COLOR_BLACK)
        pyxel.rect(outer_x, outer_y, outer_width, outer_height, pyxel.COLOR_NAVY)

        # inner border
        inner_margin = 4
        inner_x = outer_x + inner_margin
        inner_y = outer_y + inner_margin
        inner_width = outer_width - inner_margin * 2
        inner_height = outer_height - inner_margin * 2

        pyxel.rect(inner_x, inner_y, inner_width, inner_height, pyxel.COLOR_DARK_BLUE)
        pyxel.text(pyxel.width // 2 - 40 // 2, inner_y + 8, "ENTER NAME", pyxel.COLOR_WHITE)


        # textbox part
        textbox_width = 140
        textbox_height = 16
        textbox_x = pyxel.width // 2 - textbox_width // 2
        textbox_y = inner_y + 24

        pyxel.rect(textbox_x - 1, textbox_y - 1, textbox_width + 2, textbox_height + 2, pyxel.COLOR_WHITE)
        pyxel.rect(textbox_x, textbox_y, textbox_width, textbox_height, pyxel.COLOR_BLACK)

        # blinking _ effect thingyy
        cursor = "_" if pyxel.frame_count % 30 < 15 else ""
        display_text = name + cursor
        text_x = pyxel.width // 2 - (len(display_text) * 4) // 2
        pyxel.text(text_x, textbox_y + 5, display_text, pyxel.COLOR_YELLOW)

        pyxel.text(pyxel.width // 2 - 44 // 2, inner_y + 50, "PRESS ENTER", pyxel.COLOR_LIGHT_BLUE)

    def draw_leaderboard(self, state, page, split_normal, split_hard):
        min_x = pyxel.width // 2 - 100
        min_y = pyxel.height // 2 - 100
        max_y = pyxel.height // 2 + 100
        spacing = BlOCK_SIZE + PADDING
        mode = "CAMPAIGN" if state else "ENDLESS"

        pyxel.rect(min_x - 1, min_y - 1, 202, 202, pyxel.COLOR_NAVY)
        pyxel.rect(min_x, min_y, 200, 200, pyxel.COLOR_DARK_BLUE)
        create_text(f"LEADERBOARD: {mode}".center(25), pyxel.width // 2 - 10, min_y + 3, pyxel.COLOR_YELLOW, pyxel.COLOR_ORANGE)
        pyxel.blt(pyxel.width // 2 + 45, min_y + 3, 0, 0, 208, 16, 16, 0)
        
        state_y = min_y + spacing + 5
        start_1y = state_y + 1
        start_2y = state_y + 1
        start_1x = min_x + 5
        end_1x = pyxel.width // 2 - 19
        start_2x = end_1x + 16 + 4
        end_2x = pyxel.width // 2 + 100 - 5 - 16
        center_1x = pyxel.width // 2 - 47
        center_2x = pyxel.width // 2 + 47

        create_text("EXIT", 21, 6, pyxel.COLOR_PINK, pyxel.COLOR_RED)

        create_text("NORMAL".center(8), center_1x, state_y, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)

        if split_normal:
            for i, player_data in enumerate(split_normal[page - 1]):
                name = player_data["name"]
                exp = player_data["exp"]
                rounds = player_data["rounds"]

                create_text(f"{name}".ljust(20), center_1x, start_1y + spacing * 1, pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
                create_text(f"EXP LEFT: {exp}".ljust(20), center_1x, start_1y + spacing * 2, pyxel.COLOR_LIGHT_BLUE, pyxel.COLOR_NAVY)
                create_text(f"ROUNDS SURVIVED: {rounds}".ljust(20), center_1x, start_1y + spacing * 3, pyxel.COLOR_PEACH, pyxel.COLOR_BROWN)

                start_1y = start_1y + spacing * 3 + 3

        create_text("HARD".center(8), center_2x, state_y, pyxel.COLOR_CYAN, pyxel.COLOR_NAVY)

        if split_hard:
            for i, player_data in enumerate(split_hard[page - 1]):
                name = player_data["name"]
                exp = player_data["exp"]
                rounds = player_data["rounds"]

                create_text(f"{name}".ljust(20), center_2x, start_2y + spacing * 1, pyxel.COLOR_WHITE, pyxel.COLOR_BLACK)
                create_text(f"EXP LEFT: {exp}".ljust(20), center_2x, start_2y + spacing * 2, pyxel.COLOR_LIGHT_BLUE, pyxel.COLOR_NAVY)
                create_text(f"ROUNDS SURVIVED: {rounds}".ljust(20), center_2x, start_2y + spacing * 3, pyxel.COLOR_PEACH, pyxel.COLOR_BROWN)

                start_2y = start_2y + spacing * 3 + 3

        pyxel.blt(pyxel.width // 2 - 16, max_y - 13, 0, 16, 208, 16, 16, 0)
        pyxel.blt(pyxel.width // 2, max_y - 13, 0, 32, 208, 16, 16, 0)

        


            

