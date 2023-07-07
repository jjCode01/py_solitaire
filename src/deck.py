import random
from typing import Iterable
from src.card import Card


class EmptyDeck(Exception):
    pass


class Deck:
    """Deck object for card games"""

    def __init__(self, cards: list[Card], num_of_decks: int = 1, shuffled=False):
        self.num_of_decks = num_of_decks
        self.cards: list[Card] = cards
        if shuffled:
            self.shuffle()
        self.uid = hash((card.face + card.suit for card in self.cards))

    def __len__(self) -> int:
        return len(self.cards)

    def __getitem__(self, key: int) -> Card:
        if not self.cards:
            raise EmptyDeck("Deck is empty")
        if not isinstance(key, int):
            raise ValueError("ValueError: key must be an integer")
        if key >= len(self.cards):
            raise IndexError("IndexError: key out of range of Deck length")

        return self.cards[key]

    def __iter__(self) -> Iterable[Card]:
        for card in self.cards:
            yield card

    def __add__(self, other_deck: "Deck") -> None:
        if not isinstance(other_deck, Deck):
            raise ValueError(
                f"ValueError: cannot add {type(other_deck)} to Deck object"
            )

        self.cards += other_deck.cards

    def __bool__(self) -> bool:
        return len(self.cards) > 0

    def __hash__(self) -> int:
        return hash(tuple(self.cards))

    def deal_card(self, face_down: bool = False) -> Card:
        if not self.cards:
            raise EmptyDeck("Deck is out of cards")

        card = self.cards.pop()
        card.face_down = face_down
        return card

    def shuffle(self) -> None:
        random.shuffle(self.cards)
