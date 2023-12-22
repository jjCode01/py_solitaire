from copy import deepcopy
from io import StringIO
from os import name, system
from time import sleep

from src.card import Card
from src.card_types import get_playing_cards
from src.deck import Deck
from src.exceptions import EndGame, NewGame, WinGame
from src.stack import Stack

GAME_TYPES = {"1": "klondike", "2": "yukon"}
PLAY_OPTIONS = {
    "klondike": ["[d] to draw cards", "[u] undo", "[n] new game", "[q] to quit"],
    "yukon": ["[u] undo", "[n] new game", "[q] to quit"],
}


class Solitaire:
    """A class to represent a game of solitaire"""

    ACES = ["S", "C", "D", "H"]
    KINGS = ["1", "2", "3", "4", "5", "6", "7"]
    PULL = "P"
    prev_state: dict

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
            pull_cards_cnt = max(len(self.stacks["P"]) * -1, -3)
            white_space: int = pull_cards_cnt * -1 * 6 + 7
            if not self.stacks["P"]:
                tableau.write("\n\n")
                if self.deck:
                    tableau.write(f"\n{self.deck.cards[-1].back_img} ")
                else:
                    tableau.write("\n      ")
            else:
                tableau.write(f"\n{'|  P  |':>{white_space}}\n")
                tableau.write(f"{'+-----+':>{white_space}}\n")
                if self.deck:
                    tableau.write(f"{self.deck.cards[-1].back_img} ")
                else:
                    tableau.write("      ")
                for i in range(pull_cards_cnt, 0):
                    tableau.write(f" {self.stacks['P'].cards[i].img}")
            tableau.write("\n")

        return tableau.getvalue()

    def __hash__(self) -> int:
        return hash(tuple(self.stacks))

    def _refresh(self, memo: str = "", show_options: bool = True) -> None:
        _ = system("cls") if name == "nt" else system("clear")
        print(self)
        print(memo)
        if show_options:
            print("Options:", " | ".join(PLAY_OPTIONS[self.type]))

    def _draw_aces_row(self):
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

    def _set_prev_state(self) -> None:
        self.prev_state = {
            "stacks": {},
            "draw_cards": self.stacks["P"].cards[:],
            "deck_cards": self.deck.cards[:],
            "moves": self.moves,
        }
        for stack in self.KINGS + self.ACES:
            self.prev_state["stacks"][stack] = deepcopy(self.stacks[stack].cards)

    def _check_win(self) -> bool:
        if self.deck or self.stacks["P"]:
            return False
        for i in self.KINGS:
            stack = self.stacks[i]
            if not stack:
                continue
            if stack.cards[0].face_down:
                return False
            for n, card in enumerate(self.stacks[i].cards[1:], 1):
                prev_card = self.stacks[i].cards[n - 1]
                if not _is_valid_king_position(prev_card, card):
                    return False

        self._finish_game()
        return True

    def _move_stack(self, move_from_stack: str, move_to_stack: str) -> bool:
        if move_from_stack.upper() not in self.stacks:
            return False
        if move_to_stack.upper() not in self.stacks:
            return False
        to_stack: Stack = self.stacks[move_to_stack.upper()]
        from_stack: Stack = self.stacks[move_from_stack.upper()]
        available_moves = to_stack.valid_moves(from_stack)

        if not available_moves:
            return False
        if len(available_moves) == 1:
            start_index = available_moves[0]
        elif len(available_moves) > 1:
            s = "\n".join(
                [
                    f"{i}: {from_stack.cards[card_index].img}"
                    for i, card_index in enumerate(available_moves, 1)
                ]
            )
            while True:
                try:
                    move_choice = int(input(s + "\nEnter Choice: "))
                except ValueError:
                    continue
                else:
                    try:
                        start_index = available_moves[move_choice - 1]
                    except IndexError:
                        continue
                    else:
                        break
            #     move_choice = input(s + "\nEnter Choice: ")
            #     if move_choice.isnumeric():
            #         move_choice_int = int(move_choice)
            #     if not move_choice.isnumeric():
            #         continue
            #     if 1 > int(move_choice) >= len(available_moves) + 1:
            #         continue
            #     break

            # start_index = available_moves[int(move_choice) - 1]
        else:
            return False

        self._set_prev_state()
        self.moves += 1
        to_stack.add(*from_stack.pop(start_index))

        if from_stack:
            from_stack.cards[-1].face_down = False

        return True

    def _pull_cards(self) -> None:
        if len(self.deck) >= 3:
            self.stacks["P"].cards += self.deck.cards[:3]
            self.deck.cards = self.deck.cards[3:]

        elif 0 < len(self.deck) < 3:
            self.stacks["P"].cards += self.deck.cards[:]
            self.deck.cards = []

        elif not self.deck and self.stacks["P"]:
            self.deck.cards = self.stacks["P"].cards[:]
            self.stacks["P"].clear()
            self._pull_cards()

    def _init_tableau(self) -> None:
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

    def _undo(self) -> None:
        if self.prev_state:
            for stack in self.KINGS + self.ACES:
                self.stacks[stack].cards = self.prev_state["stacks"][stack][:]
            self.stacks["P"].cards = self.prev_state["draw_cards"][:]
            self.deck.cards = self.prev_state["deck_cards"][:]
            self.moves = self.prev_state["moves"]

    def _process_command(self, command: str) -> str:
        def move_to_ace(command: str) -> str:
            card = self.stacks[command.upper()].cards[-1]
            if self._move_stack(command, card.suit):
                if self._check_win():
                    raise WinGame
                return "Nice Move!"
            return "Invalid Move. Try again..."

        match command:
            case "q":  # quit game
                if input("Are you sure you want to quit? [y]: ").upper() == "Y":
                    raise EndGame
                return "Lets Play!"
            case "n":  # new game
                if (
                    input("Are you sure you want start a new game? [y]: ").upper()
                    == "Y"
                ):
                    raise NewGame
                return "Lets Play!"
            case "u":  # undo last move
                self._undo()
                return "Undo last move..."
            case "d" if self.type == "klondike":  # draw cards from deck
                self._set_prev_state()
                self._pull_cards()
                return "Draw cards from deck...."
            case "p" if self.type == "klondike":
                return move_to_ace(command)
            case command if command in self.KINGS and self.stacks[command]:
                return move_to_ace(command)
            case command if len(command) == 2:
                from_col = command[0]
                to_col = command[1]
                if self._move_stack(from_col, to_col):
                    if self._check_win():
                        raise WinGame
                    return "Nice Move!"
                return "Invalid Move. Try Again..."
            case _:
                return "Invalid Move. Try again..."

    def start_game(self) -> bool:
        """Start game play"""
        game_select = input("\n1: Klondike\n2: Yukon\n:")
        if game_select not in GAME_TYPES:
            self.start_game()

        self.type = GAME_TYPES[game_select]

        self._init_tableau()
        memo = "Lets Play!"

        # Game Loop
        try:
            while True:
                self._refresh(memo=memo)
                command = input("Enter move: ").lower()
                memo = self._process_command(command)
        except WinGame:
            self.win = True
            self._refresh(memo="***** YOU WIN ******", show_options=False)
            play_again = input("Plag again? [y/n] ")
            if play_again.lower() == "y":
                return True
            return False
        except NewGame:
            return True
        except EndGame:
            return False

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
                        if not self._move_stack(num, card.suit):
                            break
                        sleep(0.33)
                        self._refresh(show_options=False)


def _is_valid_king_position(upper_card: Card, lower_card: Card) -> bool:
    if upper_card.color == lower_card.color:
        return False
    if upper_card.value != lower_card.value + 1:
        return False
    return True
