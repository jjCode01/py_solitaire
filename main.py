from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter

import database as db
from solitaire import Solitaire
from modules.card import Card


def check_files() -> Path:
    data_file_path = Path.joinpath(Path.home(), "py_card_games")
    if not Path.exists(data_file_path):
        Path.mkdir(data_file_path)

    statistics_file = Path.joinpath(data_file_path, "py_card_game_statistics.txt")
    if not Path.is_file(statistics_file):
        columns = ["date", "game", "win", "length_seconds", "moves", "deck_id"]
        with open(statistics_file, "w") as f:
            f.write("\t".join(columns))
            f.write("\n")

    return data_file_path


def log_game(game: Solitaire, date: datetime, duration: int, cards: list[Card]) -> None:
    data_file_path = check_files()
    game_data_file = Path.joinpath(data_file_path, "py_card_game_data.txt")
    statistics_file = Path.joinpath(data_file_path, "py_card_game_statistics.txt")

    deck_id = hash((card for card in cards))

    with open(game_data_file, "a") as f:
        f.write(f"{deck_id}\t{cards}\n")

    game_statistics = [
        f"{date:%Y-%m-%d %H:%M}",
        game.type,
        f"{game.win}",
        f"{int(duration)}",
        f"{game.moves}",
        f"{deck_id}",
    ]

    with open(statistics_file, "a") as f:
        f.write("\t".join(game_statistics))
        f.write("\n")


def main():
    game = Solitaire()
    deck_cards = game.deck.cards[:]
    start_time = perf_counter()
    start_date = datetime.now()
    continue_play = game.start_game()
    end_time = perf_counter()
    game_duration_seconds = int(end_time - start_time)

    if game.moves > 0:
        log_game(game, start_date, game_duration_seconds, deck_cards)

        db.insert_game(
            start_date + timedelta(days=1),
            game.type,
            game.win,
            game_duration_seconds,
            game.moves,
        )

    if continue_play:
        main()


if __name__ == "__main__":
    main()
