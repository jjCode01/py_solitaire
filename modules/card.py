from dataclasses import dataclass


@dataclass
class Card:
    """Card object for card games"""

    face: str
    suit: str
    face_down: bool = False
    value: int = 0
    front_img: str = ""
    back_img: str = ""

    def __str__(self) -> str:
        if self.face_down:
            return "---"
        if len(self.face) == 2:
            return f"{self.face}{self.suit}"
        return f" {self.face}{self.suit}"

    def flip(self) -> None:
        self.face_down = not self.face_down

    def img(self) -> str:
        if self.face_down:
            return self.back_img

        return self.front_img

    @property
    def value(self) -> int:
        if self.face_down:
            return 0
        return self._value

    @value.setter
    def value(self, new_value: int) -> None:
        if not isinstance(new_value, int):
            raise ValueError(
                f"ValueError: New value must be an integer, got {new_value}"
            )

        self._value = new_value
