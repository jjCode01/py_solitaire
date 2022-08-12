from os import system, name
from random import shuffle

from modules.card_types import get_playing_cards
from modules.deck import Deck


# class Stack:
#     @staticmethod
#     def verify_val(val: int) -> None:
#         if not isinstance(val, int) or 0 >= val > 13:
#             raise ValueError(
#                 "Value Error: size argument must be an int between 1 and 13"
#             )

#     def __init__(self, val: int) -> None:
#         self.verify_val(val)
#         self._vals = [val]

#     def __len__(self) -> int:
#         return len(self._vals)

#     def __getitem__(self, index: int) -> int:
#         return self._vals[index]

#     def __add__(self, vals: list) -> None:
#         self._vals += vals


class GridGame:
    def __init__(self, size=1) -> None:
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Value Error: size argument must be a positive int")
        self.deck = Deck(get_playing_cards(), shuffled=True)
        self._set_card_values()

        self.stacks = [[] for _ in range(7)]
        self.draw_cards = []

        for i in range(7):
            self.stacks[i].append(self.deck.deal_card())

            for j in range(i + 1, 7):
                self.stacks[j].append(self.deck.deal_card(face_down=True))

        # self.stacks = [[self.deck.deal_card()] for _ in range(7)]

    def __str__(self) -> str:
        s = ""
        for col in ["A", "B", "C", "D"]:
            s += f'|{" " * (3 - len(str(col)))}{col} '
        s += "|\n"
        s += f"{'+----' * 4}+\n"
        s += f"{'|    ' * 4}"
        s += "|\n\n"

        tallest = max([len(stack) for stack in self.stacks if stack])
        for col in range(len(self.stacks)):
            s += f'|{" " * (3 - len(str(col)))}{col} '
        s += "|\n"
        s += f"{'+----' * len(self.stacks)}+\n"
        for col in range(tallest):
            for stack in self.stacks:
                if stack and col < len(stack):
                    s += f'|{" " * (3 - len(str(stack[col])))}{stack[col]} '
                else:
                    s += "|    "

            s += "|\n"

        s += "\n|  P |\n"
        s += "+----+\n"
        s += (
            "|    |"
            if not self.draw_cards
            else f'|{" " * (3 - len(str(self.draw_cards[-1])))}{self.draw_cards[-1]} |'
        )

        return s

    def _set_card_values(self) -> None:
        face_values = {
            "A": 0,
            "2": 2,
            "3": 4,
            "4": 6,
            "5": 8,
            "6": 10,
            "7": 12,
            "8": 14,
            "9": 16,
            "10": 18,
            "J": 20,
            "Q": 22,
            "K": 24,
        }

        suit_values = {"C": 0, "D": 1, "S": 0, "H": 1}

        for card in self.deck:
            print(f"{face_values.get(card.face) + suit_values[card.suit]}")
            card.value = face_values[card.face] + suit_values[card.suit]

    def move_stack(self, stack_to_move: int, move_to_stack: int) -> bool:
        if not isinstance(stack_to_move, int) or not isinstance(move_to_stack, int):
            raise ValueError("Value Error: arguments must be integers")

        if stack_to_move < 0 or move_to_stack < 0:
            raise ValueError("Value Error: arguments cannot be less than 0")

        if stack_to_move >= len(self.stacks) or move_to_stack >= len(self.stacks):
            raise IndexError("Index Error: arguments exceed number of stacks")

        if stack_to_move == move_to_stack:
            return False

        print(
            f"{self.stacks[stack_to_move][0].value} -> {self.stacks[move_to_stack][-1].value}"
        )

        for i, card in enumerate(self.stacks[stack_to_move]):
            if not self.stacks[stack_to_move]:
                return False

            if card.face_down:
                continue

            _ = input(
                f"Checking {card} [{card.value}] -> {self.stacks[move_to_stack][-1]} [{self.stacks[move_to_stack][-1].value}]"
            )

            if (
                (not self.stacks[move_to_stack] and card.face == "K")
                or (card.value == self.stacks[move_to_stack][-1].value - 1)
                or (card.value == self.stacks[move_to_stack][-1].value - 3)
            ):
                stack = self.stacks[stack_to_move][i:]
                self.stacks[stack_to_move] = self.stacks[stack_to_move][:i]

                if self.stacks[stack_to_move]:
                    self.stacks[stack_to_move][-1].face_down = False

                self.stacks[move_to_stack] += stack
                return True

        return False

    def pull_cards(self) -> None:
        if len(self.deck) >= 3:
            self.draw_cards += self.deck.cards[-3:]
            self.deck = self.deck.cards[:-3]

        if 0 < len(self.deck) < 3:
            self.draw_cards += self.deck.cards[:]
            self.deck.cards = []

        if not self.deck and self.draw_cards:
            self.deck.cards = self.draw_cards[:]
            self.draw_cards = []
            self.pull_cards()

    def start_game(self) -> None:
        # playing = True
        memo = "Lets Play!"

        # Game Loop
        while True:
            clear()
            print(self)
            print(memo)
            menu_select = input("[m] to move -- [d] to draw cards -- [q] to quit: ")
            if menu_select == "q":
                break
            elif menu_select == "m":
                col_to_move = input("Pick a column to move, or q to quit: ")
                move_to_col = input("Pick a column to move it to: ")
                try:
                    int(move_to_col)
                except ValueError:
                    memo = "Invalid Entry, Try Again"
                    continue

                if self.move_stack(int(col_to_move), int(move_to_col)):
                    memo = "Nice Play!"
                else:
                    memo = "Invalid Move, Try Again!"

            elif menu_select == "d":
                self.pull_cards()


def main():
    game = GridGame()
    game.start_game()


def clear():
    """Clear terminal"""
    # 'nt' = windows; 'posix' = linux or mac
    _ = system("cls") if name == "nt" else system("clear")


if __name__ == "__main__":
    main()
