# main.py file: GUI for the SOS Game using tkinter

import tkinter as tk
from tkinter import ttk, messagebox
from game_logic import SimpleSOSGame, GeneralSOSGame  # Import game logic classes for two game modes

class SOSApp:
    def __init__(self, root):
        """
        Initialize the main SOS game app.
        :param root: Tkinter root window
        """
        self.root = root
        self.root.title("SOS Game")  # Set window title
        self.create_widgets()        # Build all UI components
        self.on_start_new_game()     # Start a new game immediately on launch

    def create_widgets(self):
        """
        Create and arrange all the GUI widgets including player options, board size,
        game mode selection, and control buttons.
        """
        top_frame = ttk.Frame(self.root, padding=8)
        top_frame.grid(row=0, column=0, sticky="ew")  # Top container for player and settings

        # --- Red Player Controls ---
        red_frame = ttk.LabelFrame(top_frame, text="Red Player", padding=6)
        red_frame.grid(row=0, column=0, padx=(4, 20))
        self.red_letter_var = tk.StringVar(value="S")  # Default letter selection for red player
        ttk.Radiobutton(red_frame, text="S", variable=self.red_letter_var, value="S").grid(row=0, column=0)
        ttk.Radiobutton(red_frame, text="O", variable=self.red_letter_var, value="O").grid(row=0, column=1)

        # --- Center Controls: Board size, Mode, New Game button ---
        center_frame = ttk.Frame(top_frame)
        center_frame.grid(row=0, column=1)
        ttk.Label(center_frame, text="Board size:").grid(row=0, column=0)
        self.size_var = tk.IntVar(value=3)  # Default board size
        ttk.Spinbox(center_frame, from_=3, to=12, width=5, textvariable=self.size_var).grid(row=0, column=1, padx=(5,15))
        ttk.Label(center_frame, text="Mode:").grid(row=0, column=2)
        self.mode_var = tk.StringVar(value="simple")  # Default mode
        ttk.Radiobutton(center_frame, text="Simple", variable=self.mode_var, value="simple").grid(row=0, column=3)
        ttk.Radiobutton(center_frame, text="General", variable=self.mode_var, value="general").grid(row=0, column=4)
        ttk.Button(center_frame, text="New Game", command=self.on_start_new_game).grid(row=0, column=5, padx=(15,0))

        # --- Blue Player Controls ---
        blue_frame = ttk.LabelFrame(top_frame, text="Blue Player", padding=6)
        blue_frame.grid(row=0, column=2, padx=(20,4))
        self.blue_letter_var = tk.StringVar(value="S")  # Default letter selection for blue player
        ttk.Radiobutton(blue_frame, text="S", variable=self.blue_letter_var, value="S").grid(row=0, column=0)
        ttk.Radiobutton(blue_frame, text="O", variable=self.blue_letter_var, value="O").grid(row=0, column=1)

        # --- Labels to display turn and score ---
        self.turn_label = ttk.Label(self.root, text="", font=("Arial",11,"bold"))
        self.turn_label.grid(row=1, column=0, pady=(4,4))
        self.score_label = ttk.Label(self.root, text="", font=("Arial",10,"bold"))
        self.score_label.grid(row=2, column=0, pady=(0,4))

        # --- Frame to hold the game board buttons ---
        self.board_frame = ttk.Frame(self.root, padding=8)
        self.board_frame.grid(row=3, column=0)

    def on_start_new_game(self):
        """
        Start a new game based on selected mode and board size.
        Initializes the appropriate game logic class.
        """
        mode = self.mode_var.get()
        size = self.size_var.get()
        if mode == "simple":
            self.game = SimpleSOSGame(size)
        else:
            self.game = GeneralSOSGame(size)
        self.build_board_ui()  # Build the board UI whenever a new game starts

    def build_board_ui(self):
        """
        Build the board UI dynamically based on the game board size.
        Initializes buttons for each cell and prepares canvas for drawing SOS lines.
        """
        # Clear previous board if exists
        for w in self.board_frame.winfo_children():
            w.destroy()

        size = self.game.board_size
        self.cell_size = 60
        self.cell_buttons = [[None]*size for _ in range(size)]

        # Canvas for drawing SOS lines
        self.canvas = tk.Canvas(self.board_frame, width=size*self.cell_size,
                                height=size*self.cell_size, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=size, rowspan=size)

        # Create a button for each cell in the board
        for r in range(size):
            for c in range(size):
                btn = tk.Button(self.board_frame, text="", width=4, height=2, font=("Arial",12,"bold"),
                                command=lambda rr=r, cc=c: self.on_cell_clicked(rr,cc))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.cell_buttons[r][c] = btn

        # Update initial labels
        self.update_turn_label()
        self.update_score_label()

    def on_cell_clicked(self, r, c):
        """
        Handle a cell click: make a move, update UI, draw SOS lines, and handle endgame.
        """
        if self.game.game_over:
            return

        # Determine current player's selected letter
        letter = self.red_letter_var.get() if self.game.current_turn == "red" else self.blue_letter_var.get()

        # Attempt to make move in game logic; return if invalid
        if not self.game.make_move(r, c, letter):
            return

        # Update UI after move
        self.update_cell_ui(r, c)
        self.update_turn_label()
        self.update_score_label()

        # Draw any SOS lines formed
        if self.game.last_sos_lines:
            self.draw_sos_lines(self.game.last_sos_lines, self.game.last_move_player)

        # Handle game over scenarios
        if isinstance(self.game, SimpleSOSGame):
            if self.game.winner:
                messagebox.showinfo("Game Over", f"{self.game.winner.capitalize()} wins by forming SOS!")
                self.disable_board()
            elif self.game.is_board_full():  # <-- Draw check fixed
                messagebox.showinfo("Game Over", "It's a draw!")
                self.disable_board()
        elif isinstance(self.game, GeneralSOSGame) and self.game.game_over:
            self.show_general_result()

    def draw_sos_lines(self, lines, player):
        """
        Draw lines connecting the SOS pattern on the board.
        :param lines: list of tuples representing line endpoints
        :param player: the player who formed the SOS
        """
        color = "blue" if player == "blue" else "red"
        for r1, c1, r2, c2 in lines:
            x1 = c1*self.cell_size + self.cell_size//2
            y1 = r1*self.cell_size + self.cell_size//2
            x2 = c2*self.cell_size + self.cell_size//2
            y2 = r2*self.cell_size + self.cell_size//2
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3)

    def update_cell_ui(self, r, c):
        """
        Update the text and color of a board cell based on game state.
        """
        val = self.game.get_cell(r, c)
        btn = self.cell_buttons[r][c]
        btn.config(text=val if val else "")
        owner = self.game.get_cell_owner(r, c)
        if owner == "red":
            btn.config(fg="red")
        elif owner == "blue":
            btn.config(fg="blue")
        else:
            btn.config(fg="black")

    def update_turn_label(self):
        """Update the label showing whose turn it is."""
        self.turn_label.config(text=f"Current turn: {self.game.current_turn}")

    def update_score_label(self):
        """Update the score label for General mode; empty for Simple mode."""
        if isinstance(self.game, GeneralSOSGame):
            self.score_label.config(text=f"Blue: {self.game.scores['blue']} | Red: {self.game.scores['red']}")
        else:
            self.score_label.config(text="")

    def show_general_result(self):
        """
        Show game result for General mode when the board is full.
        Determines winner or draw and disables the board.
        """
        blue, red = self.game.scores["blue"], self.game.scores["red"]
        if blue > red:
            winner = "Blue"
        elif red > blue:
            winner = "Red"
        else:
            winner = None
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins with higher score!")
        else:
            messagebox.showinfo("Game Over", "It's a draw!")
        self.disable_board()

    def disable_board(self):
        """Disable all board buttons to prevent further moves."""
        for row in self.cell_buttons:
            for btn in row:
                btn.config(state="disabled")

def main():
    """Main function to launch the SOS game app."""
    root = tk.Tk()
    app = SOSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
