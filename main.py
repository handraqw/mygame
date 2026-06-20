from core.game import Game
from config import SCREEN_WIDTH, SCREEN_HEIGHT


def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.run()


if __name__ == '__main__':
    main()
