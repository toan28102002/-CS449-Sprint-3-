# game_logic.py file: Core logic for the SOS game
from typing import List, Optional

# ---------------- Base Class ----------------
class BaseSOSGame:
    """Common functionality for all SOS games"""

    def __init__(self, board_size: int = 3):
        """
        Initialize the base game with board size and reset the game state.
        :param board_size: Size of the board (minimum 3x3)
        """
        self.board_size = max(3, int(board_size))
        self.reset_game()

    def reset_game(self):
        """Reset the board and all game state variables."""
        # 2D list representing the board cells; None = empty
        self.board: List[List[Optional[str]]] = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]
        self.current_turn = "blue"  # Starting player
        self.move_count = 0
        self.game_over = False
        self.last_sos_lines = []  # Tracks SOS lines formed in last move
        self.last_move_player = None  # Which player made the last move
        # Owner of each cell ("blue" or "red") for coloring purposes
        self.owner_board: List[List[Optional[str]]] = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]

    def in_bounds(self, r, c):
        """Check if row and column are inside the board boundaries."""
        return 0 <= r < self.board_size and 0 <= c < self.board_size

    def cell_empty(self, r, c):
        """Check if a cell is valid and currently empty."""
        return self.in_bounds(r, c) and self.board[r][c] is None

    def toggle_turn(self):
        """Switch turn from one player to the other."""
        self.current_turn = "red" if self.current_turn == "blue" else "blue"

    def get_cell(self, r, c):
        """Return the value of a cell ('S', 'O', or None) if in bounds."""
        return None if not self.in_bounds(r, c) else self.board[r][c]

    def get_cell_owner(self, r, c):
        """Return which player owns the cell ('blue', 'red', or None)."""
        if not self.in_bounds(r, c):
            return None
        return self.owner_board[r][c]

    def check_for_sos(self, r, c) -> List[tuple]:
        """
        Check if placing a letter at (r, c) forms any SOS.
        Returns a list of SOS lines represented as tuples (r1, c1, r2, c2).
        Only checks in four directions (horizontal, vertical, two diagonals).
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        sos_lines = []

        for dr, dc in directions:
            if self.form_sos(r, c, dr, dc):
                sos_lines.append((r, c, r + 2*dr, c + 2*dc))
            if self.form_sos(r, c, -dr, -dc):
                sos_lines.append((r, c, r - 2*dr, c - 2*dc))
        return sos_lines

    def form_sos(self, r, c, dr, dc) -> bool:
        """
        Check if the 3-cell line starting at (r,c) in direction (dr,dc) is SOS.
        Returns True if it forms SOS.
        """
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
    """Simple mode: first player to form SOS wins"""
    
    def __init__(self, board_size: int = 3):
        super().__init__(board_size)
        self.winner: Optional[str] = None  # Tracks winner in Simple mode

    def make_move(self, r, c, letter: str) -> bool:
        """
        Attempt to place a letter at (r, c).
        Returns True if move was successful.
        Ends the game immediately if SOS is formed.
        """
        if self.game_over:
            return False
        letter = letter.strip().upper()
        if letter not in ("S", "O") or not self.cell_empty(r, c):
            return False

        self.board[r][c] = letter
        self.move_count += 1
        self.owner_board[r][c] = self.current_turn
        self.last_move_player = self.current_turn

        # Check for SOS
        sos_lines = self.check_for_sos(r, c)
        self.last_sos_lines = sos_lines

        if sos_lines:
            self.winner = self.current_turn
            self.game_over = True  # End game immediately
            return True

        self.toggle_turn()
        return True

# ---------------- General Game ----------------
class GeneralSOSGame(BaseSOSGame):
    """General mode: score points for each SOS formed"""

    def __init__(self, board_size: int = 3):
        super().__init__(board_size)
        self.scores = {"blue": 0, "red": 0}  # Tracks score per player

    def make_move(self, r, c, letter: str) -> bool:
        """
        Attempt to place a letter at (r, c).
        Scores points for each SOS formed.
        The game ends when the board is full.
        """
        if self.game_over:
            return False
        letter = letter.strip().upper()
        if letter not in ("S", "O") or not self.cell_empty(r, c):
            return False

        self.board[r][c] = letter
        self.move_count += 1
        self.owner_board[r][c] = self.current_turn
        self.last_move_player = self.current_turn

        # Check for SOS and add to current player's score
        sos_lines = self.check_for_sos(r, c)
        self.last_sos_lines = sos_lines
        if sos_lines:
            self.scores[self.current_turn] += len(sos_lines)

        self.toggle_turn()  # Switch turns

        # End game if board is full
        if self.move_count >= self.board_size * self.board_size:
            self.game_over = True

        return True
