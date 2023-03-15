from os import system, name
from copy import deepcopy
from enum import Enum
from time import sleep

from modules.card_types import get_playing_cards
from modules.deck import Deck
from modules.card import Card

PLAY_OPTIONS = {
    "classic": ["[d] to draw cards", "[u] undo", "[n] new game", "[q] to quit"],
    "yukon": ["[u] undo", "[n] new game", "[q] to quit"],
}

ACES = ["S", "C", "D", "H"]
KINGS = ["1", "2", "3", "4", "5", "6", "7"]


class Solitaire:
    def __init__(self, game_type: str = "classic") -> None:
        if game_type.lower() not in ("classic", "yukon"):
            raise ValueError("Invalid Game Type")
        self.type: str = game_type.lower()
        self.deck: Deck = Deck(
            get_playing_cards(card_values=list(range(13))), shuffled=True
        )
        self.stacks: dict[str, list[Card]] = {i: [] for i in KINGS + ACES}
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

        tallest = max((len(y) for x, y in self.stacks.items() if x in KINGS))
        tallest = max((13, tallest))
        for col in KINGS:
            board += f"|  {col}  "
        board += "|\n"
        board += f"{'+-----' * 7}+\n"
        for row in range(tallest):
            for col in KINGS:
                if self.stacks.get(col) and row < len(self.stacks[col]):
                    card: Card = self.stacks[col][row]
                    board += f"|{card.img}"
                else:
                    board += "|     "

            board += "|\n"

        if self.type == "classic":
            board += f"\n|  P  |  Deck: {len(self.deck)}\n"
            board += "+-----+\n"

            board += (
                "|     |\n" if not self.draw_cards else f"|{self.draw_cards[-1].img}|\n"
            )

        return board

    def _draw_aces_row(self) -> str:
        board = ""

        # Aces Row
        for col in ACES:
            board += f"|  {col}  "
        board += f"|\n{'+-----' * 4}+\n"
        for col in ACES:
            if self.stacks[col]:
                card = self.stacks[col][-1]
                board += f"|{card.img}"
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
        for i in KINGS:
            could_win = True
            stack = self.stacks[i]
            if not stack:
                continue
            if stack[0].face_down:
                break
            if not stack[0].face == "K":
                break
            for n, card in enumerate(self.stacks[i][1:], 1):
                prev_card = self.stacks[i][n - 1]
                if not is_valid_position(prev_card, card):
                    could_win = False
                    break
            if not could_win:
                break
        else:
            self._finish_game()
            return True

        for i in KINGS:
            if self.stacks[i]:
                return False
        return True

    def move_stack(self, stack_to_move: str, move_to_stack: str) -> bool:
        def _king_to_empty(move_card: Card, to_stack: str) -> bool:
            if not move_card.face == "K":
                return False
            if not to_stack in KINGS:
                return False
            if self.stacks[to_stack]:
                return False
            return True

        def _stack_to_stack(card: Card, to_stack: str) -> bool:
            if not to_stack in KINGS:
                return False
            if not self.stacks[to_stack]:
                return False
            return is_valid_position(self.stacks[to_stack][-1], card)

        def _verify_play(move_card: Card, to_stack: str) -> bool:
            if (
                _king_to_empty(move_card, to_stack)
                or _stack_to_stack(move_card, to_stack)
                or (
                    to_stack in ACES
                    and not self.stacks[to_stack]
                    and move_card.face == "A"
                )
                or (
                    to_stack in ACES
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

        if stack_to_move == move_to_stack:
            return False

        if stack_to_move == "P":
            if not self.draw_cards:
                return False

            if _verify_play(self.draw_cards[-1], move_to_stack):
                self.stacks[move_to_stack].append(self.draw_cards.pop())
                return True

        elif stack_to_move in ACES:
            if self.stacks.get(stack_to_move) is None:
                return False
            card = self.stacks[stack_to_move][-1]
            if _verify_play(card, move_to_stack):
                self.stacks[move_to_stack].append(self.stacks[stack_to_move].pop())
                return True
            return False

        elif stack_to_move in KINGS:
            if self.stacks.get(stack_to_move) is None:
                return False

            if move_to_stack in ACES:
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
                    [f"{i}: {card[1].img}" for i, card in enumerate(possible_moves)]
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
        player_wins = False

        # Game Loop
        while True:
            clear()
            print(self)
            print(memo)
            print("Options:", " | ".join(PLAY_OPTIONS[self.type]))
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
            elif len(menu_select) == 1 and menu_select in KINGS:
                if self.stacks[menu_select]:
                    card = self.stacks[menu_select][-1]
                    if self.move_stack(menu_select, card.suit):
                        if self.check_win():
                            player_wins = True
                        else:
                            memo = "Nice Play!"

                    else:
                        memo = "Invalid Move, Try Again!"

            elif len(menu_select) == 2:
                col_to_move = menu_select[0]
                move_to_col = menu_select[1]

                if self.move_stack(col_to_move, move_to_col):
                    if self.check_win():
                        player_wins = True
                    else:
                        memo = "Nice Play!"

                else:
                    memo = "Invalid Move, Try Again!"

            if player_wins:
                self._finish_game()
                clear()
                print(self)
                print("***** YOU WIN ******")
                play_again = input("Plag again? [y/n] ")
                if play_again.lower() == "y":
                    continue_play = True
                break

        if continue_play:
            main()

    def _finish_game(self):
        while True:
            for stack in KINGS:
                if self.stacks[stack]:
                    break
            else:
                break

            for num, stack in self.stacks.items():
                if num in KINGS and stack:
                    while True:
                        if not stack:
                            break
                        card = stack[-1]
                        if not self.move_stack(num, card.suit):
                            break
                        sleep(0.4)
                        clear()
                        print(self)


def is_valid_position(upper_card: Card, lower_card: Card) -> bool:
    if upper_card.color == lower_card.color:
        return False
    if upper_card.value != lower_card.value + 1:
        return False
    return True


def main():
    game_types = {"1": "classic", "2": "yukon"}
    game_select = input("\n1: Classic Solitair\n2: Yukon Solitair\n:")
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
