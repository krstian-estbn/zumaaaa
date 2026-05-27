import pyxel
from utils import Color, Orientation


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

        """
        n = len("Press [P] to play.")
        pyxel.rect(pyxel.width // 2 - (4 * n) // 2 - 2, pyxel.height // 2 - 20 - 2, n * 4 + 3, 9, pyxel.COLOR_GRAY)
        pyxel.text(pyxel.width // 2 - (4 * n) // 2, pyxel.height // 2 - 20, "Press [P] to play.", pyxel.COLOR_BLACK)
        """

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

    def draw_game_over(self):
        pyxel.text(pyxel.width // 2 - (4 * len("GAME OVER")) // 2, pyxel.height // 2, "GAME OVER", pyxel.COLOR_WHITE)

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
        



