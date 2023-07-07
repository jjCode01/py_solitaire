from src.solitaire import Solitaire


def main():
    game = Solitaire()
    continue_play = game.start_game()
    if continue_play:
        main()


if __name__ == "__main__":
    main()
