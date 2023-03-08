from os import system, name
from copy import deepcopy

from modules.card_types import get_playing_cards
from modules.deck import Deck
from modules.card import Card


def _card_str(card: Card) -> str:
    if card.face_down:
        return "\033[48;5;20m --- \033[m"

    SUIT_IMAGES = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
    if card.face == "10":
        return f"{_card_color(card)} {card.face}{SUIT_IMAGES[card.suit]} \033[m"
    return f"{_card_color(card)}  {card.face}{SUIT_IMAGES[card.suit]} \033[m"


def _card_color(card: Card) -> str:
    if card.face_down:
        return "\033[48;5;20m"

    if card.suit in ("H", "D"):
        return "\033[48;5;15m\033[38;5;124m"

    return "\033[48;5;15m\033[38;5;236m"


_play_options = {
    "classic": ["[d] to draw cards", "[u] undo", "[n] new game", "[q] to quit"],
    "yukon": ["[u] undo", "[n] new game", "[q] to quit"],
}


class Solitaire:
    def __init__(self, game_type: str = "classic") -> None:
        if game_type.lower() not in ("classic", "yukon"):
            raise ValueError("Invalid Game Type")
        self.type: str = game_type.lower()
        self.deck: Deck = Deck(
            get_playing_cards(card_values=list(range(13))), shuffled=True
        )
        self.stacks: dict[str, list[Card]] = {i: [] for i in "1234567ABCD"}
        self.draw_cards = []

        for i in range(1, 8):
            self.stacks[str(i)].append(self.deck.deal_card())

            for j in range(i + 1, 8):
                self.stacks[str(j)].append(self.deck.deal_card(face_down=True))

        if self.type == "yukon":
            for _ in range(4):
                for i in range(2, 8):
                    self.stacks[str(i)].append(self.deck.deal_card())

        self.prev_state = {}

    def __str__(self) -> str:
        board = self._draw_aces_row()

        tallest = max((len(y) for x, y in self.stacks.items() if x in "1234567"))
        tallest = max((13, tallest))
        for col in "1234567":
            board += f"|  {col}  "
        board += "|\n"
        board += f"{'+-----' * 7}+\n"
        for row in range(tallest):
            for col in "1234567":
                if self.stacks.get(col) and row < len(self.stacks[col]):
                    card: Card = self.stacks[col][row]
                    board += f"|{_card_str(card)}"
                else:
                    board += "|     "

            board += "|\n"

        if self.type == "classic":
            board += f"\n|  P  |  Deck: {len(self.deck)}\n"
            board += "+-----+\n"

            board += (
                "|     |\n"
                if not self.draw_cards
                else f"|{_card_str(self.draw_cards[-1])}|\n"
            )

        return board

    def _draw_aces_row(self) -> str:
        board = ""

        # Aces Row
        for col in "ABCD":
            board += f"|  {col}  "
        board += f"|\n{'+-----' * 4}+\n"
        for col in "ABCD":
            if self.stacks[col]:
                card = self.stacks[col][-1]
                board += f"|{_card_str(card)}"
            else:
                board += "|     "
        board += "|\n\n"
        return board

    def set_prev_state(self) -> None:
        self.prev_state = {
            "stacks": deepcopy(self.stacks),
            "draw_cards": self.draw_cards[:],
            "deck_cards": self.deck.cards[:],
        }

    def check_win(self) -> bool:
        if self.deck or self.draw_cards:
            return False
        for i in "1234567":
            if self.stacks[i]:
                return False
        return True

    def move_stack(self, stack_to_move: str, move_to_stack: str) -> bool:
        def _verify_play(move_card: Card, to_stack: str) -> bool:
            if (
                (
                    to_stack in "1234567"
                    and not self.stacks[to_stack]
                    and move_card.face == "K"
                )
                or (
                    to_stack in "1234567"
                    and self.stacks[to_stack]
                    and move_card.value == self.stacks[to_stack][-1].value - 1
                    and suit_values[move_card.suit]
                    != suit_values[self.stacks[to_stack][-1].suit]
                )
                or (
                    to_stack in "ABCD"
                    and not self.stacks[to_stack]
                    and move_card.face == "A"
                )
                or (
                    to_stack in "ABCD"
                    and self.stacks[to_stack]
                    and move_card.suit == self.stacks[to_stack][-1].suit
                    and move_card.value == self.stacks[to_stack][-1].value + 1
                )
            ):
                self.set_prev_state()
                return True
            return False

        stack_to_move = stack_to_move.upper()
        move_to_stack = move_to_stack.upper()

        suit_values = {"C": 0, "D": 1, "S": 0, "H": 1}

        if stack_to_move == move_to_stack:
            return False

        if stack_to_move == "P":
            if not self.draw_cards:
                return False

            if _verify_play(self.draw_cards[-1], move_to_stack):
                self.stacks[move_to_stack].append(self.draw_cards.pop())
                return True

        elif stack_to_move in "ABCD":
            if self.stacks.get(stack_to_move) is None:
                return False
            card = self.stacks[stack_to_move][-1]
            if _verify_play(card, move_to_stack):
                self.stacks[move_to_stack].append(self.stacks[stack_to_move].pop())
                return True
            return False

        elif stack_to_move in "1234567":
            if self.stacks.get(stack_to_move) is None:
                return False

            if move_to_stack in "ABCD":
                card = self.stacks[stack_to_move][-1]
                if _verify_play(card, move_to_stack):
                    self.stacks[move_to_stack].append(self.stacks[stack_to_move].pop())
                    if self.stacks[stack_to_move]:
                        self.stacks[stack_to_move][-1].face_down = False
                    return True
                return False

            possible_moves = [
                (i, card)
                for i, card in enumerate(self.stacks.get(stack_to_move, []))
                if not card.face_down and _verify_play(card, move_to_stack)
            ]

            if len(possible_moves) == 1:
                move_card = possible_moves[0][0]

            elif len(possible_moves) > 1:
                s = "\n".join(
                    [
                        f"{i}: {_card_str(card[1])}"
                        for i, card in enumerate(possible_moves)
                    ]
                )
                while True:
                    move_choice = input(s + "\nEnter Choice: ")
                    if move_choice.isnumeric() and 0 <= int(move_choice) < len(
                        possible_moves
                    ):
                        break

                move_card = possible_moves[int(move_choice)][0]

            else:
                return False

            self.set_prev_state()
            stack = self.stacks[stack_to_move][move_card:]
            self.stacks[stack_to_move] = self.stacks[stack_to_move][:move_card]

            if self.stacks[stack_to_move]:
                self.stacks[stack_to_move][-1].face_down = False

            self.stacks[move_to_stack] += stack
            return True
        return False

    def pull_cards(self) -> None:
        if len(self.deck) >= 3:
            self.draw_cards += self.deck.cards[:3]
            self.deck.cards = self.deck.cards[3:]

        elif 0 < len(self.deck) < 3:
            self.draw_cards += self.deck.cards[:]
            self.deck.cards = []

        elif not self.deck and self.draw_cards:
            self.deck.cards = self.draw_cards[:]
            self.draw_cards = []
            self.pull_cards()

    def start_game(self) -> None:
        memo = "Lets Play!"
        continue_play = False

        # Game Loop
        while True:
            clear()
            print(self)
            print(memo)
            print("Options:", " | ".join(_play_options[self.type]))
            menu_select = input("Enter move: ")
            menu_select = menu_select.lower()
            if menu_select == "q":
                break
            elif menu_select == "n":
                continue_play = True
                break
            elif menu_select == "u" and self.prev_state:
                self.stacks = self.prev_state["stacks"].copy()
                self.draw_cards = self.prev_state["draw_cards"][:]
                self.deck.cards = self.prev_state["deck_cards"][:]
                memo = "Undo last move..."
            elif menu_select == "d" and self.type == "classic":
                memo = "Cards drawn..."
                self.set_prev_state()
                self.pull_cards()
            elif len(menu_select) == 2:
                col_to_move = menu_select[0]
                move_to_col = menu_select[1]

                if self.move_stack(col_to_move, move_to_col):
                    if self.check_win():
                        clear()
                        print(self)
                        print("***** YOU WIN ******")
                        play_again = input("Plag again? [y/n] ")
                        if play_again.lower() == "y":
                            continue_play = True
                        break
                    else:
                        memo = "Nice Play!"

                else:
                    memo = "Invalid Move, Try Again!"

        if continue_play:
            main()


def main():
    game_types = {"1": "classic", "2": "yukon"}
    game_select = input("1: Classic Solitair\n2: Yukon Solitair\n:")
    if not game_select in ("1", "2"):
        main()

    game = Solitaire(game_types[game_select])
    game.start_game()


def clear():
    """Clear terminal"""
    # 'nt' = windows; 'posix' = linux or mac
    _ = system("cls") if name == "nt" else system("clear")


if __name__ == "__main__":
    main()
