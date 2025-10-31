import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class GUIRenderer:
    def __init__(self, battle_state, placeholder_path="assets/placeholder.png"):
        self.battle_state = battle_state
        self.root = tk.Tk()
        self.root.title("Pokémon Battle")

        # --- Window setup ---
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self.root.configure(bg="#f8f8f8")

        # --- Image setup ---
        self.base_sprite_size = 320
        self.placeholder_img_front = Image.open("blastoise.png").resize((self.base_sprite_size, self.base_sprite_size))
        self.placeholder_img_back = Image.open("charizard_back.png").resize((self.base_sprite_size, self.base_sprite_size))
        self.placeholder_photo_front = ImageTk.PhotoImage(self.placeholder_img_front)
        self.placeholder_photo_back = ImageTk.PhotoImage(self.placeholder_img_back)

        # --- UI setup ---
        self._setup_ui()

        # Track player’s selected move
        self.selected_move = None

        # Enable resize
        self.root.bind("<Configure>", self._on_resize)

    # ============================================================
    # 🧱 UI SETUP
    # ============================================================
    def _setup_ui(self):
        """Initialize layout for both Pokémon and control buttons."""
        # Turn label
        self.turn_label = tk.Label(self.root, text="Turn 1", font=("Arial", 14, "bold"), bg="#f8f8f8")
        self.turn_label.pack(pady=10)

        # --- Top Pokémon (AI) ---
        self.p2_frame = tk.Frame(self.root, bg="#f8f8f8")
        self.p2_frame.pack(pady=10)

        self.p2_label = tk.Label(self.p2_frame, text=f"{self.battle_state.pokemon2.species.name}",
                                 font=("Arial", 12), bg="#f8f8f8")
        self.p2_label.pack()

        self.p2_image = tk.Label(self.p2_frame, image=self.placeholder_photo_front, bg="#f8f8f8")
        self.p2_image.pack()

        self.p2_hp = ttk.Progressbar(self.p2_frame, length=220)
        self.p2_hp.pack(pady=5)
        self.p2_hp["maximum"] = self.battle_state.pokemon2.stats["hp"]
        self.p2_hp["value"] = self.battle_state.pokemon2.current_hp

        # --- Bottom Pokémon (Player) ---
        self.p1_frame = tk.Frame(self.root, bg="#f8f8f8")
        self.p1_frame.pack(pady=30)

        self.p1_label = tk.Label(self.p1_frame, text=f"{self.battle_state.pokemon1.species.name}",
                                 font=("Arial", 12), bg="#f8f8f8")
        self.p1_label.pack()

        self.p1_image = tk.Label(self.p1_frame, image=self.placeholder_photo_back, bg="#f8f8f8")
        self.p1_image.pack()

        self.p1_hp = ttk.Progressbar(self.p1_frame, length=220)
        self.p1_hp.pack(pady=5)
        self.p1_hp["maximum"] = self.battle_state.pokemon1.stats["hp"]
        self.p1_hp["value"] = self.battle_state.pokemon1.current_hp

        # --- Message box ---
        self.message_label = tk.Label(self.root, text="", font=("Consolas", 12),
                                      bg="#e0e0e0", width=90, height=4,
                                      anchor="w", justify="left")
        self.message_label.pack(pady=10)

        # --- Move selection frame ---
        self.move_frame = tk.Frame(self.root, bg="#dfe6e9")
        self.move_frame.pack(pady=10)

        self.move_buttons = []
        self._create_move_buttons()

    def _create_move_buttons(self):
        """Create 4 move buttons for the player."""
        moves = self.battle_state.pokemon1.moves
        for i, move in enumerate(moves[:4]):  # max 4 moves like real Pokémon
            btn = tk.Button(
                self.move_frame,
                text=f"{move.name} ({move.move_type})",
                font=("Arial", 11, "bold"),
                width=18,
                height=2,
                bg="#a29bfe",
                activebackground="#6c5ce7",
                command=lambda m=move: self._select_move(m)
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=8)
            self.move_buttons.append(btn)

    # ============================================================
    # 🧩 Event Handlers
    # ============================================================
    def _select_move(self, move):
        """Called when player clicks a move button."""
        self.selected_move = move
        self.show_message(f"You selected {move.name}!")

    def wait_for_move(self):
        """Block until player selects a move (used by game loop)."""
        self.selected_move = None
        self.show_message("Choose your move...")
        while self.selected_move is None:
            self.root.update()
        return self.selected_move

    def _on_resize(self, event):
        """Resize Pokémon sprites on window resize."""
        new_width, new_height = event.width, event.height
        scale_factor = min(new_width / 900, new_height / 600)
        new_size = int(self.base_sprite_size * scale_factor)
        new_size = max(180, min(new_size, 500))

        front_resized = self.placeholder_img_front.resize((new_size, new_size))
        back_resized = self.placeholder_img_back.resize((new_size, new_size))

        self.placeholder_photo_front = ImageTk.PhotoImage(front_resized)
        self.placeholder_photo_back = ImageTk.PhotoImage(back_resized)

        self.p2_image.config(image=self.placeholder_photo_front)
        self.p1_image.config(image=self.placeholder_photo_back)

    # ============================================================
    # 🔄 Dynamic Updates
    # ============================================================
    def update_hp(self):
        self.p1_hp["value"] = max(0, self.battle_state.pokemon1.current_hp)
        self.p2_hp["value"] = max(0, self.battle_state.pokemon2.current_hp)
        self.root.update_idletasks()

    def show_message(self, text):
        self.message_label.config(text=text)
        self.root.update_idletasks()

    def update_turn(self, turn):
        self.turn_label.config(text=f"Turn {turn}")
        self.root.update_idletasks()

    def render_frame(self):
        self.root.update()

    def close(self):
        self.root.destroy()
