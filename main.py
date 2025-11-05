#main.py file:
import tkinter as tk
from tkinter import ttk, messagebox
from game_logic import SimpleSOSGame, GeneralSOSGame

class SOSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SOS Game")
        self.create_widgets()
        self.on_start_new_game()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding=8)
        top_frame.grid(row=0, column=0, sticky="ew")

        # Red player
        red_frame = ttk.LabelFrame(top_frame, text="Red Player", padding=6)
        red_frame.grid(row=0, column=0, padx=(4, 20))
        self.red_letter_var = tk.StringVar(value="S")
        ttk.Radiobutton(red_frame, text="S", variable=self.red_letter_var, value="S").grid(row=0, column=0)
        ttk.Radiobutton(red_frame, text="O", variable=self.red_letter_var, value="O").grid(row=0, column=1)

        # Center controls
        center_frame = ttk.Frame(top_frame)
        center_frame.grid(row=0, column=1)
        ttk.Label(center_frame, text="Board size:").grid(row=0, column=0)
        self.size_var = tk.IntVar(value=3)
        ttk.Spinbox(center_frame, from_=3, to=12, width=5, textvariable=self.size_var).grid(row=0, column=1, padx=(5,15))
        ttk.Label(center_frame, text="Mode:").grid(row=0, column=2)
        self.mode_var = tk.StringVar(value="simple")
        ttk.Radiobutton(center_frame, text="Simple", variable=self.mode_var, value="simple").grid(row=0, column=3)
        ttk.Radiobutton(center_frame, text="General", variable=self.mode_var, value="general").grid(row=0, column=4)
        ttk.Button(center_frame, text="New Game", command=self.on_start_new_game).grid(row=0, column=5, padx=(15,0))

        # Blue player
        blue_frame = ttk.LabelFrame(top_frame, text="Blue Player", padding=6)
        blue_frame.grid(row=0, column=2, padx=(20,4))
        self.blue_letter_var = tk.StringVar(value="S")
        ttk.Radiobutton(blue_frame, text="S", variable=self.blue_letter_var, value="S").grid(row=0, column=0)
        ttk.Radiobutton(blue_frame, text="O", variable=self.blue_letter_var, value="O").grid(row=0, column=1)

        # Labels
        self.turn_label = ttk.Label(self.root, text="", font=("Arial",11,"bold"))
        self.turn_label.grid(row=1, column=0, pady=(4,4))
        self.score_label = ttk.Label(self.root, text="", font=("Arial",10,"bold"))
        self.score_label.grid(row=2, column=0, pady=(0,4))
        self.board_frame = ttk.Frame(self.root, padding=8)
        self.board_frame.grid(row=3, column=0)

    def on_start_new_game(self):
        mode = self.mode_var.get()
        size = self.size_var.get()
        if mode == "simple":
            self.game = SimpleSOSGame(size)
        else:
            self.game = GeneralSOSGame(size)
        self.build_board_ui()

    def build_board_ui(self):
        for w in self.board_frame.winfo_children():
            w.destroy()

        size = self.game.board_size
        self.cell_size = 60
        self.cell_buttons = [[None]*size for _ in range(size)]
        self.canvas = tk.Canvas(self.board_frame, width=size*self.cell_size,
                                height=size*self.cell_size, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=size, rowspan=size)

        for r in range(size):
            for c in range(size):
                btn = tk.Button(self.board_frame, text="", width=4, height=2, font=("Arial",12,"bold"),
                                command=lambda rr=r, cc=c: self.on_cell_clicked(rr,cc))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.cell_buttons[r][c] = btn

        self.update_turn_label()
        self.update_score_label()

    def on_cell_clicked(self, r, c):
        if self.game.game_over:
            return

        letter = self.red_letter_var.get() if self.game.current_turn == "red" else self.blue_letter_var.get()
        if not self.game.make_move(r, c, letter):
            return

        self.update_cell_ui(r, c)
        self.update_turn_label()
        self.update_score_label()

        # Draw SOS lines
        if self.game.last_sos_lines:
            self.draw_sos_lines(self.game.last_sos_lines, self.game.last_move_player)

        # Handle game over
        if isinstance(self.game, SimpleSOSGame) and self.game.winner:
            messagebox.showinfo("Game Over", f"{self.game.winner.capitalize()} wins by forming SOS!")
            self.disable_board()
        elif isinstance(self.game, GeneralSOSGame) and self.game.game_over:
            self.show_general_result()

    def draw_sos_lines(self, lines, player):
        color = "blue" if player == "blue" else "red"
        for r1, c1, r2, c2 in lines:
            x1 = c1*self.cell_size + self.cell_size//2
            y1 = r1*self.cell_size + self.cell_size//2
            x2 = c2*self.cell_size + self.cell_size//2
            y2 = r2*self.cell_size + self.cell_size//2
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3)

    def update_cell_ui(self, r, c):
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
        self.turn_label.config(text=f"Current turn: {self.game.current_turn}")

    def update_score_label(self):
        if isinstance(self.game, GeneralSOSGame):
            self.score_label.config(text=f"Blue: {self.game.scores['blue']} | Red: {self.game.scores['red']}")
        else:
            self.score_label.config(text="")

    def show_general_result(self):
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
        for row in self.cell_buttons:
            for btn in row:
                btn.config(state="disabled")

def main():
    root = tk.Tk()
    app = SOSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
