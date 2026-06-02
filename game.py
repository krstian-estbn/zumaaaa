from model.model import Model
from view import View
from controller import Controller

import pyxel

if __name__ == '__main__':
    pyxel.init(208, 208, title="Zuma: Tower Defense Game")
    model = Model()  # logic
    view = View()  # what the user sees
    controller = Controller(model, view)  # glues model & view

    controller.start_game()