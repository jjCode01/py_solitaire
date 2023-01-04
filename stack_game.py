from os import system, name

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


class GridGame:
    def __init__(self, yukon=False) -> None:
        self.deck = Deck(get_playing_cards(), shuffled=True)
        self._set_card_values()

        self.stacks2 = {i: [] for i in "1234567ABCD"}
        self.draw_cards = []

        for i in range(1, 8):
            self.stacks2[str(i)].append(self.deck.deal_card())

            for j in range(i + 1, 8):
                self.stacks2[str(j)].append(self.deck.deal_card(face_down=True))

        if yukon:
            for _ in range(4):
                for i in range(2, 8):
                    self.stacks2[str(i)].append(self.deck.deal_card())

    def __str__(self) -> str:
        s = ""

        # Aces Row
        for col in "ABCD":
            s += f"|  {col}  "
        s += f"|\n{'+-----' * 4}+\n"
        for col in "ABCD":
            if self.stacks2[col]:
                card = self.stacks2.get(col)[-1]
                s += f"|{_card_str(card)}"
            else:
                s += "|     "
        s += "|\n\n"

        tallest = max((len(y) for x, y in self.stacks2.items() if x in "1234567"))
        for col in "1234567":
            s += f"|  {col}  "
        s += "|\n"
        s += f"{'+-----' * 7}+\n"
        for row in range(tallest):
            for col in "1234567":
                if self.stacks2.get(col) and row < len(self.stacks2.get(col)):
                    card: Card = self.stacks2.get(col)[row]
                    s += f"|{_card_str(card)}"
                else:
                    s += "|     "

            s += "|\n"

        s += f"\n|  P  |  Deck: {len(self.deck)}\n"
        s += "+-----+\n"

        s += (
            "|     |\n"
            if not self.draw_cards
            else f"|{_card_str(self.draw_cards[-1])}|\n"
        )

        return s

    def _set_card_values(self) -> None:
        face_values = {
            "A": 0,
            "2": 1,
            "3": 2,
            "4": 3,
            "5": 4,
            "6": 5,
            "7": 6,
            "8": 7,
            "9": 8,
            "10": 9,
            "J": 10,
            "Q": 11,
            "K": 12,
        }

        for card in self.deck:
            card.value = face_values[card.face]

    def move_stack(self, stack_to_move: str, move_to_stack: str) -> bool:
        def _verify_play(move_card: Card, to_stack: str) -> bool:
            if (
                (
                    to_stack in "1234567"
                    and not self.stacks2[to_stack]
                    and move_card.face == "K"
                )
                or (
                    to_stack in "1234567"
                    and self.stacks2[to_stack]
                    and move_card.value == self.stacks2[to_stack][-1].value - 1
                    and suit_values[move_card.suit]
                    != suit_values[self.stacks2[to_stack][-1].suit]
                )
                or (
                    to_stack in "ABCD"
                    and not self.stacks2[to_stack]
                    and move_card.face == "A"
                )
                or (
                    to_stack in "ABCD"
                    and self.stacks2[to_stack]
                    and move_card.suit == self.stacks2[to_stack][-1].suit
                    and move_card.value == self.stacks2[to_stack][-1].value + 1
                )
            ):
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
                self.stacks2[move_to_stack].append(self.draw_cards.pop())
                return True

        elif stack_to_move in "ABCD":
            if self.stacks2.get(stack_to_move) is None:
                return False
            card = self.stacks2[stack_to_move][-1]
            if _verify_play(card, move_to_stack):
                self.stacks2[move_to_stack].append(self.stacks2[stack_to_move].pop())
                return True
            return False

        elif stack_to_move in "1234567":
            if self.stacks2.get(stack_to_move) is None:
                return False

            if move_to_stack in "ABCD":
                card = self.stacks2[stack_to_move][-1]
                if _verify_play(card, move_to_stack):
                    self.stacks2[move_to_stack].append(
                        self.stacks2[stack_to_move].pop()
                    )
                    if self.stacks2[stack_to_move]:
                        self.stacks2[stack_to_move][-1].face_down = False
                    return True
                return False

            possible_moves = [
                (i, card)
                for i, card in enumerate(self.stacks2.get(stack_to_move, []))
                if not card.face_down and _verify_play(card, move_to_stack)
            ]

            if not possible_moves:
                return False

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

            stack = self.stacks2[stack_to_move][move_card:]
            self.stacks2[stack_to_move] = self.stacks2[stack_to_move][:move_card]

            if self.stacks2[stack_to_move]:
                self.stacks2[stack_to_move][-1].face_down = False

            self.stacks2[move_to_stack] += stack
            return True

            # for i, card in enumerate(self.stacks2.get(stack_to_move, [])):

            #     if card.face_down:
            #         continue

            #     if _verify_play(card, move_to_stack):
            #         stack = self.stacks2[stack_to_move][i:]
            #         self.stacks2[stack_to_move] = self.stacks2[stack_to_move][:i]

            #         if self.stacks2[stack_to_move]:
            #             self.stacks2[stack_to_move][-1].face_down = False

            #         self.stacks2[move_to_stack] += stack
            #         return True
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
            menu_select = input(
                "Enter move -- [d] to draw cards -- [n] new game -- [q] to quit: "
            )
            menu_select = menu_select.lower()
            if menu_select == "q":
                break
            elif menu_select == "n":
                continue_play = True
                break
            elif menu_select == "d":
                memo = "Cards drawn..."
                self.pull_cards()
            elif len(menu_select) == 2:
                col_to_move = menu_select[0]
                move_to_col = menu_select[1]

                if self.move_stack(col_to_move, move_to_col):
                    memo = "Nice Play!"

                else:
                    memo = "Invalid Move, Try Again!"

        if continue_play:
            main()


def main():
    game_select = input("1: Regular Solitair\n2: Yukon Solitair\n:")
    if not game_select in ("1", "2"):
        main()

    game = GridGame(game_select == "2")
    game.start_game()


def clear():
    """Clear terminal"""
    # 'nt' = windows; 'posix' = linux or mac
    _ = system("cls") if name == "nt" else system("clear")


if __name__ == "__main__":
    main()
