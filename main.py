from src.game import Game
from src.constants import GAME_TITLE, VERSION

def main():
    print(f"Starting {GAME_TITLE} v{VERSION}")
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
    