import random
from modules.card import Card


class Deck:
    """Deck object for card games"""

    def __init__(self, cards: list[Card], num_of_decks: int = 1, shuffled=False):
        self.num_of_decks = num_of_decks

        # populate Deck with Card objects
        self.cards: list[Card] = cards

        # shuffle Deck
        if shuffled:
            self.shuffle()

    def __len__(self) -> int:
        return len(self.cards)

    def __getitem__(self, key: int) -> Card:
        if not self.cards:
            raise IndexError("IndexError: Deck is empty")
        if not isinstance(key, int):
            raise ValueError("ValueError: key must be an integer")
        if key >= len(self.cards):
            raise IndexError("IndexError: key out of range of Deck length")

        return self.cards[key]

    def __iter__(self) -> Card:
        for card in self.cards:
            yield card

    def __add__(self, other_deck) -> None:
        if not isinstance(other_deck, Deck):
            raise ValueError(
                f"ValueError: cannot add {other_deck.type()} to Deck object"
            )

        self.cards += other_deck.cards

    def __bool__(self) -> bool:
        return len(self.cards) > 0

    def deal_card(self, face_down: bool = False) -> object:
        if len(self.cards) > 0:
            card = self.cards.pop()
            card.face_down = face_down
            return card

    def shuffle(self) -> None:
        random.shuffle(self.cards)
