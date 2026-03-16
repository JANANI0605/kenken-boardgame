# KenKen Puzzle — Pygame Edition

A fully playable **KenKen** math-logic puzzle game built with Python and Pygame. Puzzles are procedurally generated so you get a fresh challenge every time.

---

## What is KenKen?

KenKen is a number puzzle played on an N×N grid. The rules are simple:

- Fill every row with the numbers **1 to N**, each exactly once.
- Fill every column with the numbers **1 to N**, each exactly once.
- Every bold-bordered group of cells (called a **cage**) shows a target number and an operator. The numbers in that cage must produce the target using that operator.
  - `6×` → the cells multiply to 6
  - `9+` → the cells add up to 9
  - `2−` → the larger minus the smaller equals 2
  - `3÷` → the larger divided by the smaller equals 3
- A single-cell cage just shows the number that goes there directly.

---

## Requirements

- Python 3.8 or newer
- Pygame

Install Pygame with:

```bash
pip install pygame
```

---

## Running the Game

```bash
python kenken_pygame.py
```

The window opens immediately. Click **Generate** to create your first puzzle.

---

## How to Play

### Mouse
| Action | How |
|---|---|
| Select a cell | Click it |
| Enter a number | Click a cell, then click a number on the on-screen numpad |
| Erase a cell | Click the **⌫ ERASE** button on the numpad |

### Keyboard
| Key | Action |
|---|---|
| `1` – `N` | Enter that number into the selected cell |
| `Backspace` / `Delete` | Erase the selected cell |
| `Arrow keys` | Move selection up / down / left / right |

---

## Interface

```
┌─────────────────────────────────────────────────────┐
│  [3×3 ▾]  [Easy ▾]  [Generate]  [Check]  [Solve]   Playing  KENKEN │
├──────────────────────────────────┬──────────────────┤
│                                  │  NUMBERS         │
│         Puzzle Grid              │  [1][2][3][4]    │
│      (centred in window)         │  [5][6]          │
│                                  │  [⌫ ERASE]      │
│                                  │                  │
│                                  │  SESSION         │
│                                  │  Time   12s      │
│                                  │  Moves  5        │
│                                  │  Grid   4×4      │
│                                  │  Cages  8        │
│                                  │  Diff   Medium   │
└──────────────────────────────────┴──────────────────┘
```

### Grid
- Cage boundaries are drawn in **yellow**.
- The cage hint (e.g. `12+`) appears in the top-left corner of each cage.
- The selected cell is highlighted in blue-grey.
- After clicking **Check**, correct cells turn **green** and wrong cells turn **red**.

### Buttons
| Button | What it does |
|---|---|
| **Generate** | Creates a brand-new puzzle with the chosen size and difficulty |
| **Check** | Highlights every filled cell as correct (green) or wrong (red) |
| **Solve** | Reveals the complete solution |

### Status (top-right, next to KENKEN logo)
Shows the current game state: `Press Generate to start`, `Playing`, `Solved!`, or the check result (`✓ 8  correct    ✗ 2  wrong`).

---

## Options

### Grid Size
| Option | Grid | Cells |
|---|---|---|
| 3×3 | 3 rows × 3 cols | 9 |
| 4×4 | 4 rows × 4 cols | 16 |
| 5×5 | 5 rows × 5 cols | 25 |
| 6×6 | 6 rows × 6 cols | 36 |

### Difficulty
| Level | Cage size | Operators |
|---|---|---|
| Easy | Up to 2 cells | `+` and `−` only |
| Medium | Up to 3 cells | `+`, `−`, `×` |
| Hard | Up to 4 cells | `+`, `−`, `×`, `÷` |

---

## Win Screen

When you fill the grid correctly, a win overlay appears showing your **time** and **move count**. Click **New Puzzle** to jump straight into another game.

---

## Project Structure

```
kenken_pygame.py   — single-file game (all logic, UI, and puzzle generation)
README.md          — this file
```

### Key sections inside `kenken_pygame.py`

| Section | What it contains |
|---|---|
| `latin_square(n)` | Generates a valid N×N solution grid |
| `build_cages(sol, n, diff)` | Groups cells into cages and assigns operators/targets |
| `make_puzzle(n, diff)` | Top-level puzzle factory |
| `Button` | Reusable clickable button widget |
| `Dropdown` | Reusable dropdown selector widget |
| `KenKen` | Main game class — layout, drawing, input handling, game loop |

---

## License

Free to use and modify for personal and educational projects.
