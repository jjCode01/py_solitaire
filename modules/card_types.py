from pathlib import Path

from modules.card import Card

CWD = Path.cwd() / "img" / ""
IMG_PATH = CWD / "img" / "cards"


def get_playing_cards(num_of_decks: int = 1) -> list[Card]:
    faces = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
    suites = ("C", "D", "H", "S")
    return [
        Card(
            face=f,
            suit=s,
            value=0,
            front_img=Path.joinpath(IMG_PATH, f"{f}{s}.png"),
            back_img=Path.joinpath(IMG_PATH, "blue_back.png"),
        )
        for f in faces
        for s in suites
        for _ in range(num_of_decks)
    ]
