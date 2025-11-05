#game_logic.py file: 
from typing import List, Optional

# ---------------- Base Class ----------------
class BaseSOSGame:
    """Common functionality for all SOS games"""
    def __init__(self, board_size: int = 3):
        self.board_size = max(3, int(board_size))
        self.reset_game()

    def reset_game(self):
        self.board: List[List[Optional[str]]] = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]
        self.current_turn = "blue"
        self.move_count = 0
        self.game_over = False
        self.last_sos_lines = []
        self.last_move_player = None
        self.owner_board: List[List[Optional[str]]] = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]

    def in_bounds(self, r, c):
        return 0 <= r < self.board_size and 0 <= c < self.board_size

    def cell_empty(self, r, c):
        return self.in_bounds(r, c) and self.board[r][c] is None

    def toggle_turn(self):
        self.current_turn = "red" if self.current_turn == "blue" else "blue"

    def get_cell(self, r, c):
        return None if not self.in_bounds(r, c) else self.board[r][c]

    def get_cell_owner(self, r, c):
        if not self.in_bounds(r, c):
            return None
        return self.owner_board[r][c]

    def check_for_sos(self, r, c) -> List[tuple]:
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        sos_lines = []

        for dr, dc in directions:
            if self.form_sos(r, c, dr, dc):
                sos_lines.append((r, c, r + 2*dr, c + 2*dc))
            if self.form_sos(r, c, -dr, -dc):
                sos_lines.append((r, c, r - 2*dr, c - 2*dc))
        return sos_lines

    def form_sos(self, r, c, dr, dc) -> bool:
        if not (
            self.in_bounds(r, c)
            and self.in_bounds(r + dr, c + dc)
            and self.in_bounds(r + 2*dr, c + 2*dc)
        ):
            return False
        return (
            self.board[r][c] == "S"
            and self.board[r+dr][c+dc] == "O"
            and self.board[r+2*dr][c+2*dc] == "S"
        )

# ---------------- Simple Game ----------------
class SimpleSOSGame(BaseSOSGame):
    """Simple mode: first SOS wins"""
    def __init__(self, board_size: int = 3):
        super().__init__(board_size)
        self.winner: Optional[str] = None

    def make_move(self, r, c, letter: str) -> bool:
        if self.game_over:
            return False
        letter = letter.strip().upper()
        if letter not in ("S", "O") or not self.cell_empty(r, c):
            return False

        self.board[r][c] = letter
        self.move_count += 1
        self.owner_board[r][c] = self.current_turn
        self.last_move_player = self.current_turn

        sos_lines = self.check_for_sos(r, c)
        self.last_sos_lines = sos_lines

        if sos_lines:
            self.winner = self.current_turn
            self.game_over = True
            return True

        self.toggle_turn()
        return True

# ---------------- General Game ----------------
class GeneralSOSGame(BaseSOSGame):
    """General mode: score points for each SOS"""
    def __init__(self, board_size: int = 3):
        super().__init__(board_size)
        self.scores = {"blue": 0, "red": 0}

    def make_move(self, r, c, letter: str) -> bool:
        if self.game_over:
            return False
        letter = letter.strip().upper()
        if letter not in ("S", "O") or not self.cell_empty(r, c):
            return False

        self.board[r][c] = letter
        self.move_count += 1
        self.owner_board[r][c] = self.current_turn
        self.last_move_player = self.current_turn

        sos_lines = self.check_for_sos(r, c)
        self.last_sos_lines = sos_lines

        if sos_lines:
            self.scores[self.current_turn] += len(sos_lines)

        # Always toggle turn
        self.toggle_turn()

        # End game if board full
        if self.move_count >= self.board_size * self.board_size:
            self.game_over = True

        return True
