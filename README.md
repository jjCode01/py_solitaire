# py_solitaire

Play solitaire in the terminal.  
Includes the classic Klondike solitaire and Yukon solitaire.  

## Start Game Loop

Enter the following command into your terminal:

### Windows

```bash
python main.py
```

### Linux / Mac

```bash
python3 main.py
```

## Game Play

### Move Card to Ace Stack

Enter the number/letter of the column that contains the cards and press enter.

#### Examples

* '6' will move the top card from stack '6' up to the appropriate Ace pile.
* 'P' will move the top card from the draw pile up to the appropriate Ace pile (Klondike Solitaire only).

### Move Card(s) from Stack to Stack

With no space in between, enter the number/letter of the 'move from' stack followed by the number/letter of the 'move to' stack and press enter.  

#### Examples

* '72' will move the card(s) from stack '7' to stack '2'.
* 'C3' will move the top card form the Ace of Clubs pile back down to stack '3'.
* 'P4' will move the top card from the draw up to stack '4' (Klondike Solitaire only).

### Undo the Last Move

Enter 'u' and press enter to undo the last move.

### Start New Game

Enter 'n' and press enter.

### Quite Game

Enter 'q' and press enter.
