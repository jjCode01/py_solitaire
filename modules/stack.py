from modules.card import Card

class Stack:
    locations = ["ACE", "KING", "PULL"]
    def __init__(self, id: str, location: str) -> None:
        if not location in self.locations:
            raise ValueError("Invalid Stack type, must be 'ACE', 'KING', or 'PULL'")
        self.id: str = id
        self.location: str = location
        self.cards: list[Card] = []

    def __len__(self) -> int:
        return len(self.cards)
    
    def __bool__(self) -> bool:
        return len(self.cards) > 0
    

    def add(self, *cards: Card) -> None:
        for card in cards:
            if not isinstance(card, Card):
                raise ValueError("Expected argument card to be class<'Card'>")
            
            self.cards.append(card)

    def clear(self):
        self.cards = []

    def pop(self, index: int = -1) -> list[Card]:
        if self.cards and index == -1:
            return [self.cards.pop()]
        
        if not 0 <= index < len(self.cards):
            raise IndexError("index out of range")
        
        remove_cards = self.cards[index:]
        self.cards = self.cards[:index]
        return remove_cards
    
    def transfer(self, start_index: int, other: "Stack"):
        transfer_cards = self.pop(start_index)
        other.add(*transfer_cards)

def valid_move_to_ace(from_stack: Stack, to_stack: Stack) -> bool:
    if not from_stack or from_stack.location == 'ACE':
        return False
    if to_stack.id != from_stack.cards[-1].suit:
        return False
    if not to_stack:
        if from_stack.cards[-1].face == 'A':
            return True
        return False
    return from_stack.cards[-1].value == to_stack.cards[-1].value + 1