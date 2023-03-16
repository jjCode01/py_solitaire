from datetime import datetime
from pathlib import Path
from time import perf_counter

from crud import insert_game
from solitaire import Solitaire


def main():

    data_file_path = Path.joinpath(Path.home(), "py_card_games")
    if not Path.exists(data_file_path):
        Path.mkdir(data_file_path)

    statistics_file = Path.joinpath(data_file_path, "py_card_game_statistics.txt")
    if not Path.is_file(statistics_file):
        columns = ["date", "game", "win", "length_seconds", "moves", "deck_id"]
        with open(statistics_file, "w") as f:
            f.write("\t".join(columns))
            f.write("\n")

    game_data_file = Path.joinpath(data_file_path, "py_card_game_data.txt")

    game_types = {"1": "classic", "2": "yukon"}
    game_select = input("\n1: Classic Solitair\n2: Yukon Solitair\n:")
    if not game_select in ("1", "2"):
        main()

    game = Solitaire(game_types[game_select])
    deck_id = hash((card for card in game.deck.cards))
    deck_cards = "\t".join([card.face + card.suit for card in game.deck.cards])
    with open(game_data_file, "a") as f:
        f.write(f"{deck_id}\t{deck_cards}\n")

    start_time = perf_counter()
    start_date = datetime.now()
    continue_play = game.start_game()
    end_time = perf_counter()

    insert_game(
        start_date,
        game_types[game_select],
        game.win,
        int(end_time - start_time),
        game.moves,
    )

    game_statistics = [
        f"{start_date:%Y-%m-%d %H:%M}",
        game_types[game_select],
        f"{game.win}",
        f"{end_time - start_time:.2f}",
        f"{game.moves}",
        f"{deck_id}",
    ]
    with open(statistics_file, "a") as f:
        f.write("\t".join(game_statistics))
        f.write("\n")

    if continue_play:
        main()


if __name__ == "__main__":
    main()
