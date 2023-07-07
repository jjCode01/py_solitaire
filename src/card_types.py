from src.card import Card

CARD_COLORS = {
    "H": "\033[48;5;15m\033[38;5;124m",
    "D": "\033[48;5;15m\033[38;5;124m",
    "C": "\033[48;5;15m\033[38;5;236m",
    "S": "\033[48;5;15m\033[38;5;236m",
}
SUIT_IMAGES = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}


def card_img(face: str, suit: str) -> str:
    return f"{CARD_COLORS[suit]}{face+SUIT_IMAGES[suit]:>4} \033[m"


def get_playing_cards(
    num_of_decks: int = 1, card_values: list = [0] * 13
) -> list[Card]:
    faces = zip(
        ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"], card_values
    )
    suites = ("C", "D", "H", "S")
    deck = [
        Card(
            face=f,
            suit=s,
            value=v,
            front_img=card_img(f, s),
            back_img="\033[48;5;20m --- \033[m",
            # back_img=" --- ",
        )
        for f, v in faces
        for s in suites
        for _ in range(num_of_decks)
    ]
    return deck
