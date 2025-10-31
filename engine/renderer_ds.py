import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageEnhance
import time

TYPE_COLORS = {
    "Fire": "#FF7F50",
    "Water": "#6495ED",
    "Rock": "#B8A038",
    "Normal": "#A8A878",
    "Electric": "#F8D030",
    "Grass": "#78C850",
    "Steel": "#B8B8D0",
    "default": "#A29BFE"
}

class GUIRendererDS:
    def __init__(self, battle_state, bg_path="battle_bg.jpg"):
        self.battle_state = battle_state
        self.root = tk.Tk()
        self.root.title("Pokémon Battle (DS Mode)")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        # --- Load background ---
        self.bg_image = Image.open(bg_path)
        self.bg_photo = None

        # --- Pokémon sprites ---
        self.base_sprite_size = 300
        self.front_img = Image.open("blastoise.png").convert("RGBA")
        self.back_img = Image.open("charizard_back.png").convert("RGBA")

        # --- Layout containers ---
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Overlay gradient panel for UI
        self.bottom_frame = tk.Frame(self.root, bg="#222831")
        self.bottom_frame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)

        # Message box
        self.message_label = tk.Label(
            self.bottom_frame, text="", font=("Consolas", 13),
            bg="#2C2F33", fg="white", anchor="w", justify="left", padx=20
        )
        self.message_label.place(relx=0.02, rely=0.05, relwidth=0.96, relheight=0.25)

        # Move button grid
        self.move_frame = tk.Frame(self.bottom_frame, bg="#2C2F33")
        self.move_frame.place(relx=0.15, rely=0.35, relwidth=0.7, relheight=0.55)

        self.move_buttons = []
        self.selected_move = None
        self._create_move_buttons()

        # Cancel button
        self.cancel_button = tk.Button(
            self.bottom_frame, text="CANCEL", font=("Arial", 11, "bold"),
            bg="#F8C8B8", activebackground="#F4978E", command=self._cancel_selection
        )
        self.cancel_button.place(relx=0.43, rely=0.93, anchor="s")

        # Turn label
        self.turn_label = tk.Label(
            self.root, text="Turn 1", font=("Arial", 14, "bold"),
            bg="#FFFFFF", fg="black"
        )
        self.turn_label.place(relx=0.5, rely=0.03, anchor="n")

        self.root.bind("<Configure>", self._on_resize)

    # ============================================================
    # 🧱 UI ELEMENTS
    # ============================================================
    def _create_move_buttons(self):
        moves = self.battle_state.pokemon1.moves
        for i, move in enumerate(moves[:4]):
            color = TYPE_COLORS.get(move.move_type, TYPE_COLORS["default"])
            btn = tk.Button(
                self.move_frame,
                text=f"{move.name}\nPP {move.pp if hasattr(move, 'pp') else 10}\n{move.move_type}",
                font=("Arial", 11, "bold"),
                bg=color, fg="white",
                width=20, height=3,
                relief="raised",
                state=tk.DISABLED,
                command=lambda m=move: self._select_move(m)
            )
            btn.grid(row=i//2, column=i%2, padx=15, pady=10, sticky="nsew")
            self.move_buttons.append(btn)

    # ============================================================
    # 🎮 EVENT HANDLERS
    # ============================================================
    def _select_move(self, move):
        self.selected_move = move
        self.show_message(f"You selected {move.name}!")

    def _cancel_selection(self):
        self.selected_move = None
        self.show_message("Move selection canceled.")

    def wait_for_move(self):
        self.selected_move = None
        self._set_move_buttons_state(tk.NORMAL)
        self.show_message("Choose your move...")
        while self.selected_move is None:
            self.root.update()
        self._set_move_buttons_state(tk.DISABLED)
        return self.selected_move

    def _set_move_buttons_state(self, state):
        for btn in self.move_buttons:
            btn.config(state=state)

    # ============================================================
    # 🖼️ RENDERING
    # ============================================================
    def _on_resize(self, event):
        """Update layout + image scaling when window resizes."""
        w, h = event.width, event.height

        # Resize background
        bg_resized = self.bg_image.resize((w, int(h * 0.7)))
        self.bg_photo = ImageTk.PhotoImage(bg_resized)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # Rescale Pokémon
        scale_factor = min(w / 900, h / 650)
        size = max(160, int(self.base_sprite_size * scale_factor))

        front_resized = self.front_img.resize((size, size))
        back_resized = self.back_img.resize((size, size))
        front_photo = ImageTk.PhotoImage(front_resized)
        back_photo = ImageTk.PhotoImage(back_resized)

        # Draw them
        self.canvas.delete("sprites")
        self.canvas.create_image(int(w * 0.2), int(h * 0.45), image=back_photo, anchor="center", tags="sprites")
        self.canvas.create_image(int(w * 0.8), int(h * 0.25), image=front_photo, anchor="center", tags="sprites")

        # Store references
        self.front_photo = front_photo
        self.back_photo = back_photo

    # ============================================================
    # 🔄 STATE UPDATES
    # ============================================================
    def update_turn(self, turn):
        self.turn_label.config(text=f"Turn {turn}")
        self.root.update_idletasks()

    def update_hp(self):
        # Placeholder for later HP bar integration
        self.root.update_idletasks()

    def show_message(self, text, delay=0.9):
        self.message_label.config(text=text)
        self.root.update_idletasks()
        if delay > 0:
            time.sleep(delay)

    def render_frame(self):
        self.root.update()

    def close(self):
        self.root.destroy()
