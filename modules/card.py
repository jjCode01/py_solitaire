class Card:
    """Card object for card games"""

    def __init__(
        self,
        face: str,
        suit: str,
        face_down: bool = False,
        front_img: str = "",
        back_img: str = "",
        value: int = 0,
    ) -> None:
        self.face: str = face
        self.suit: str = suit
        self.face_down: bool = face_down
        self.front_img: str = front_img
        self.back_img: str = back_img
        self._value: int = int(value)

    def __eq__(self, __o: "Card") -> bool:
        return (
            self.face == __o.face
            and self.suit == __o.suit
            and self.face_down == __o.face_down
        )

    def __hash__(self) -> int:
        return hash((self.face, self.suit, self.face_down))

    def __str__(self) -> str:
        if self.face_down:
            return "---"
        if len(self.face) == 2:
            return f"{self.face}{self.suit}"
        return f" {self.face}{self.suit}"

    def flip(self) -> None:
        self.face_down = not self.face_down

    def img(self) -> str:
        return self.back_img if self.face_down else self.front_img

    @property
    def color(self) -> str:
        if self.face_down:
            return ""
        if self.suit.lower() in ("h", "d", "hearts", "diamonds"):
            return "Red"
        if self.suit.lower() in ("s", "c", "spades", "clubs"):
            return "Black"
        return ""

    @property
    def value(self) -> int:
        return 0 if self.face_down else self._value

    @value.setter
    def value(self, new_value: int) -> None:
        if not isinstance(new_value, int):
            raise ValueError(
                f"ValueError: New value must be an integer, got {new_value}"
            )

        self._value = new_value
