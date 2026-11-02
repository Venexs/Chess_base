# Chess Base

A personal chess programming project built with Python and Tkinter. This repository is an experimental implementation of a chessboard, piece movement, and basic move-validation logic.

The project is primarily intended for practising chess algorithms and GUI interaction.

## Features

- **Chessboard interface** — An 8×8 board rendered using Tkinter Canvas.
- **Piece movement** — Select pieces and move them to highlighted squares.
- **Move generation** — Basic movement logic for pawns, rooks, knights, bishops, queens, and kings.
- **Move validation** — Filters moves that would leave the moving player's king in check.
- **Captures** — Supports capturing opposing pieces.
- **Move log** — A separate scrollable window records moves and captures.
- **Piece graphics** — Uses PNG images for both sides' chess pieces.

## Requirements

- Python 3
- Pillow

Install the required external dependency:

```bash
pip install Pillow
```

Tkinter is included with most standard Python installations. On some Linux distributions, it may need to be installed separately.

## Running the Project

Clone the repository:

```bash
git clone https://github.com/Venexs/Chess_base.git
cd Chess_base
```

Run the main program:

```bash
python main.py
```

Run the command from the project root so that the program can locate the `assets` directory and `positions_val.json`.

## Project Structure

```text
Chess_base/
│
├── assets/
│   ├── bishop.png
│   ├── king.png
│   ├── knight.png
│   ├── pawn.png
│   ├── queen.png
│   ├── rook.png
│   └── other_*.png
│
├── main.py
├── coords_finder.py
├── positions_val.json
├── sidebartest.py
├── test.py
├── notes.txt
└── LICENSE
```

| File | Purpose |
|---|---|
| `main.py` | Main chessboard interface and movement logic |
| `positions_val.json` | Board-square coordinate data |
| `coords_finder.py` | Utility for retrieving the centre coordinates of a square |
| `sidebartest.py` | Scrollable log-window experiment |
| `test.py` | Separate-window positioning and logging experiment |
| `assets/` | Chess piece images |

## Implementation

The board uses Tkinter Canvas objects to represent squares and pieces. Each piece stores information such as its type, colour, and current board position through Canvas tags.

Movement calculations are handled separately for each piece type. The program identifies occupied squares, generates possible moves, and uses a check-detection routine to filter moves that would expose the player's king.

The board also maintains a move log in a second window, which is positioned alongside the main chessboard.

## Current Status

This is a work in progress and should be treated as an experimental chess implementation, not a complete chess application.

Some chess rules and game-state conditions are still missing or incomplete. The current implementation is primarily a foundation for experimenting with piece movement, board state, and move validation.

## License

This project is licensed under the MIT License.
