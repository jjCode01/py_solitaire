from dataclasses import dataclass


# @dataclass
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
        self._value: int = value

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
