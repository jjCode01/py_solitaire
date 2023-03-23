from copy import deepcopy
from io import StringIO
from os import system, name
from time import sleep

from modules.card import Card
from modules.card_types import get_playing_cards
from modules.deck import Deck
from modules.stack import Stack

GAME_TYPES = {"1": "klondike", "2": "yukon"}
PLAY_OPTIONS = {
    "klondike": ["[d] to draw cards", "[u] undo", "[n] new game", "[q] to quit"],
    "yukon": ["[u] undo", "[n] new game", "[q] to quit"],
}


class EndGame(Exception):
    pass


class NewGame(Exception):
    pass


class WinGame(Exception):
    pass




class Solitaire:

    ACES = ["S", "C", "D", "H"]
    KINGS = ["1", "2", "3", "4", "5", "6", "7"]
    PULL = "P"

    def __init__(self) -> None:
        self.type: str = ""
        self.deck: Deck = Deck(
            get_playing_cards(card_values=list(range(13))), shuffled=True
        )
        self.stacks: dict[str, Stack] = {}
        for k in self.KINGS:
            self.stacks[k] = Stack(k, "KING")
        for a in self.ACES:
            self.stacks[a] = Stack(a, "ACE")
        self.stacks["P"] = Stack("P", "PULL")
        self.moves: int = 0
        self.win: bool = False

    def __str__(self) -> str:

        tableau = StringIO()
        tableau.write(self._draw_aces_row())
        tableau.write(self._draw_kings_row())

        if self.type == "klondike":
            tableau.write(f"\n|  {self.PULL}  |  Deck: {len(self.deck)}\n+-----+\n")
            tableau.write(
                "|     |\n" if not self.stacks["P"] else f"|{self.stacks['P'].cards[-1].img}|\n"
            )

        return tableau.getvalue()

    def refresh(self, memo: str = "", show_options: bool = True) -> None:
        _ = system("cls") if name == "nt" else system("clear")
        print(self)
        print(memo)
        if show_options:
            print("Options:", " | ".join(PLAY_OPTIONS[self.type]))

    def _draw_aces_row(self) -> str:
        tableau_ace = StringIO()
        for col in self.ACES:
            tableau_ace.write(f"|{col:^5}")
        tableau_ace.write(f"|{'Moves':>17}\n")
        tableau_ace.write(f"{'+-----' * 4}+{' ' * 12}-----\n")
        for col in self.ACES:
            if self.stacks[col]:
                card = self.stacks[col].cards[-1]
                tableau_ace.write(f"|{card.img}")
            else:
                tableau_ace.write("|     ")
        tableau_ace.write(f"|{' ' * 12}{self.moves:^5,}\n\n")
        return tableau_ace.getvalue()

    def _draw_kings_row(self) -> str:
        tableau_king = StringIO()
        tallest = max((len(y) for x, y in self.stacks.items() if x in self.KINGS))
        tallest = max((13, tallest))
        for col in self.KINGS:
            tableau_king.write(f"|{col:^5}")
        tableau_king.write(f"|\n{'+-----' * 7}+\n")
        for row in range(tallest):
            for col in self.KINGS:
                if self.stacks.get(col) and row < len(self.stacks[col]):
                    card: Card = self.stacks[col].cards[row]
                    tableau_king.write(f"|{card.img}")
                else:
                    tableau_king.write("|     ")
            tableau_king.write("|\n")
        return tableau_king.getvalue()

    def set_prev_state(self) -> None:
        self.prev_state = {
            "stacks": {},
            "draw_cards": self.stacks["P"].cards[:],
            "deck_cards": self.deck.cards[:],
            "moves": self.moves,
        }
        for stack in self.KINGS + self.ACES:
            self.prev_state["stacks"][stack] = deepcopy(self.stacks[stack].cards)

    def check_win(self) -> bool:
        if self.deck or self.stacks["P"]:
            return False
        for i in self.KINGS:
            could_win = True
            stack = self.stacks[i]
            if not stack:
                continue
            if stack.cards[0].face_down:
                break
            if not stack.cards[0].face == "K":
                break
            for n, card in enumerate(self.stacks[i].cards[1:], 1):
                prev_card = self.stacks[i].cards[n - 1]
                if not is_valid_king_position(prev_card, card):
                    could_win = False
                    break
            if not could_win:
                break
        else:
            self._finish_game()
            return True

        for i in self.KINGS:
            if self.stacks[i]:
                return False
        return True
        

    def move_stack(self, move_from_stack: str, move_to_stack: str) -> bool:
        move_from_stack = move_from_stack.upper()
        move_to_stack = move_to_stack.upper()

        if move_from_stack == move_to_stack:
            return False
        if move_from_stack not in (*self.KINGS, *self.ACES, self.PULL):
            return False
        if move_to_stack not in self.KINGS + self.ACES:
            return False
        
        to_stack: Stack = self.stacks[move_to_stack]
        from_stack: Stack = self.stacks[move_from_stack]

        available_moves = to_stack.valid_moves(from_stack)

        if not available_moves:
            return False

        if len(available_moves) == 1:
            start_index = available_moves[0]
        elif len(available_moves) > 1:
            s = "\n".join(
                [f"{i}: {from_stack.cards[card_index].img}" for i, card_index in enumerate(available_moves, 1)]
            )
            while True:
                move_choice = input(s + "\nEnter Choice: ")
                if not move_choice.isnumeric():
                    continue
                if not 1 <= int(move_choice) < len(available_moves) + 1:
                    continue
                break

            start_index = available_moves[int(move_choice) - 1][0]

        else:
            return False
        
        self.set_prev_state()
        card_stack = self.stacks[move_from_stack].cards[start_index:]
        self.stacks[move_from_stack].cards = self.stacks[move_from_stack].cards[:start_index]

        if self.stacks[move_from_stack]:
            self.stacks[move_from_stack].cards[-1].face_down = False

        self.stacks[move_to_stack].cards += card_stack
        return True

    def pull_cards(self) -> None:
        if len(self.deck) >= 3:
            self.stacks["P"].cards += self.deck.cards[:3]
            self.deck.cards = self.deck.cards[3:]

        elif 0 < len(self.deck) < 3:
            self.stacks["P"].cards += self.deck.cards[:]
            self.deck.cards = []

        elif not self.deck and self.stacks["P"]:
            self.deck.cards = self.stacks["P"].cards[:]
            self.stacks["P"].clear()
            self.pull_cards()

    def init_tableau(self) -> None:
        for i in range(1, 8):
            card = self.deck.deal_card()
            self.stacks[str(i)].add(card)

            for j in range(i + 1, 8):
                card = self.deck.deal_card(face_down=True)
                self.stacks[str(j)].add(card)

        if self.type == "yukon":
            for _ in range(4):
                for i in range(2, 8):
                    card = self.deck.deal_card()
                    self.stacks[str(i)].add(card)

        self.prev_state = {}

    def undo(self) -> None:
        if self.prev_state:
            for stack in self.KINGS + self.ACES:
                self.stacks[stack].cards = self.prev_state["stacks"][stack][:]
            self.stacks["P"].cards = self.prev_state["draw_cards"][:]
            self.deck.cards = self.prev_state["deck_cards"][:]
            self.moves = self.prev_state["moves"]

    def process_command(self, command: str) -> str:
        match command:
            case "q":
                raise EndGame
            case "n":
                raise NewGame
            case "u":
                self.undo()
                return "Undo last move..."
            case "d" if self.type == "klondike":
                self.set_prev_state()
                self.pull_cards()
                return "Draw cards from deck...."
            case "p" if self.type == "klondike":
                card = self.stacks["P"].cards[-1]
                if self.move_stack(command, card.suit):
                    if self.check_win():
                        raise WinGame
                    return "Nice Move!"
                return "Invalid Move. Try again..."
            case command if command in self.KINGS and self.stacks[command]:
                card = self.stacks[command].cards[-1]
                if self.move_stack(command, card.suit):
                    if self.check_win():
                        raise WinGame
                    return "Nice Move!"
                return "Invalid Move. Try again..."
            case command if len(command) == 2:
                col_to_move = command[0]
                move_to_col = command[1]
                if self.move_stack(col_to_move, move_to_col):
                    if self.check_win():
                        raise WinGame
                    return "Nice Move!"
                return "Invalid Move. Try Again..."
            case _:
                return "Invalid Move. Try again..."

    def start_game(self) -> bool:
        game_select = input("\n1: Klondike\n2: Yukon\n:")
        if not game_select in GAME_TYPES:
            self.start_game()

        self.type = GAME_TYPES[game_select]

        self.init_tableau()
        memo = "Lets Play!"
        continue_play = False

        # Game Loop
        try:
            while True:
                self.refresh(memo=memo)
                command = input("Enter move: ").lower()
                memo = self.process_command(command)
        except WinGame:
            self.win = True
            self.refresh(memo="***** YOU WIN ******", show_options=False)
            play_again = input("Plag again? [y/n] ")
            if play_again.lower() == "y":
                continue_play = True
        except NewGame:
            continue_play = True
        except EndGame:
            pass
        return continue_play

    def _finish_game(self):
        while True:
            for stack in self.KINGS:
                if self.stacks[stack]:
                    break
            else:
                break

            for num, stack in self.stacks.items():
                if num in self.KINGS and stack:
                    while True:
                        if not stack:
                            break
                        card = stack.cards[-1]
                        if not self.move_stack(num, card.suit):
                            break
                        sleep(0.4)
                        self.refresh(show_options=False)


def is_valid_king_position(upper_card: Card, lower_card: Card) -> bool:
    if upper_card.color == lower_card.color:
        return False
    if upper_card.value != lower_card.value + 1:
        return False
    return True
