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
    
    def __hash__(self) -> int:
        return hash(tuple(self.cards))
    

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

    def valid_moves(self, from_stack: "Stack") -> list:
        if not from_stack.cards:
            return []
        if self.location == "ACE":
            return valid_move_to_ace(from_stack, self)
        if self.location == "KING":
            return valid_move_to_king(from_stack, self)
        return []

def valid_move_to_ace(from_stack: Stack, to_stack: Stack) -> list:
    if valid_ace_order(to_stack, from_stack.cards[-1]):
        return [len(from_stack.cards) - 1]
    return []

def valid_move_to_king(from_stack: Stack, to_stack: Stack) -> list:
    if from_stack.location != "KING":
        if valid_king_order(to_stack, from_stack.cards[-1]):
            return [len(from_stack.cards) - 1]
        return []
    
    valid_moves = []
    for i, card in enumerate(from_stack.cards):
        if not card.face_down and valid_king_order(to_stack, card):
            valid_moves.append(i)
    return valid_moves

def valid_ace_order(ace_stack: Stack, card: Card) -> bool:
    if card.suit != ace_stack.id:
        return False
    if not ace_stack and card.face == "A":
        return True
    if ace_stack and card.value == ace_stack.cards[-1].value + 1:
        return True
    return False

def valid_king_order(king_stack: Stack, card: Card) -> bool:
    if not king_stack.cards and card.face == "K":
        return True
    if king_stack.cards and card.color == king_stack.cards[-1].color:
        return False
    if king_stack.cards and card.value == king_stack.cards[-1].value - 1:
        return True
    return False