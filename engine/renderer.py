import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class GUIRenderer:
    def __init__(self, battle_state, placeholder_path="assets/placeholder.png"):
        self.battle_state = battle_state
        self.root = tk.Tk()
        self.root.title("Pokémon Battle")

        # Window setup
        self.root.geometry("900x600")
        self.root.minsize(700, 400)
        self.root.configure(bg="#f8f8f8")

        # Allow window resizing
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Bind resizing event
        self.root.bind("<Configure>", self._on_resize)


        # Load placeholder image (used for both Pokémon)
        self.placeholder_img_front = Image.open("blastoise.png").resize((200, 200))
        self.placeholder_img_back = Image.open("charizard_back.png").resize((200, 200))
        self.placeholder_photo_front = ImageTk.PhotoImage(self.placeholder_img_front)
        self.placeholder_photo_back = ImageTk.PhotoImage(self.placeholder_img_back)

        # Layout
        self._setup_ui()

    def _setup_ui(self):
        """Initialize static layout for both Pokémon."""
        # Turn label
        self.turn_label = tk.Label(
            self.root, text="Turn 1", font=("Arial", 14, "bold"), bg="#f8f8f8"
        )
        self.turn_label.pack(pady=10)

        # === Top Pokémon (Enemy) ===
        self.p2_frame = tk.Frame(self.root, bg="#f8f8f8")
        self.p2_frame.pack(pady=10)

        self.p2_label = tk.Label(
            self.p2_frame, text=f"{self.battle_state.pokemon2.species.name}", font=("Arial", 12), bg="#f8f8f8"
        )
        self.p2_label.pack()

        self.p2_image = tk.Label(self.p2_frame, image=self.placeholder_photo_front, bg="#f8f8f8")
        self.p2_image.pack()

        self.p2_hp = ttk.Progressbar(self.p2_frame, length=200)
        self.p2_hp.pack(pady=5)
        self.p2_hp["maximum"] = self.battle_state.pokemon2.stats["hp"]
        self.p2_hp["value"] = self.battle_state.pokemon2.current_hp

        # === Bottom Pokémon (Player) ===
        self.p1_frame = tk.Frame(self.root, bg="#f8f8f8")
        self.p1_frame.pack(pady=40)

        self.p1_label = tk.Label(
            self.p1_frame, text=f"{self.battle_state.pokemon1.species.name}", font=("Arial", 12), bg="#f8f8f8"
        )
        self.p1_label.pack()

        self.p1_image = tk.Label(self.p1_frame, image=self.placeholder_photo_back, bg="#f8f8f8")
        self.p1_image.pack()

        self.p1_hp = ttk.Progressbar(self.p1_frame, length=200)
        self.p1_hp.pack(pady=5)
        self.p1_hp["maximum"] = self.battle_state.pokemon1.stats["hp"]
        self.p1_hp["value"] = self.battle_state.pokemon1.current_hp

        # === Message box ===
        self.message_label = tk.Label(
            self.root, text="", font=("Consolas", 12), bg="#f0f0f0", width=80, height=3, anchor="w", justify="left"
        )
        self.message_label.pack(fill="x", padx=20, pady=10)

        # === Move buttons ===
        self.moves_frame = tk.Frame(self.root, bg="#e8e8e8")
        self.moves_frame.pack(fill="x", pady=10)

        self.move_buttons = []
        for move in self.battle_state.pokemon1.moves:
            btn = tk.Button(
                self.moves_frame,
                text=move.name,
                font=("Arial", 10, "bold"),
                width=15,
                bg="#dfe8ff",
                relief="raised",
                cursor="hand2",
            )
            btn.pack(side="left", padx=10, pady=5)
            self.move_buttons.append(btn)

        # Message box
        self.message_label = tk.Label(
            self.root, text="", font=("Consolas", 12), bg="#f0f0f0", width=80, height=4, anchor="w", justify="left"
        )
        self.message_label.pack(pady=10)

    # ------------------------
    # 🔄 Dynamic Updates
    # ------------------------
    def update_hp(self):
        """Update HP bars after damage."""
        self.p1_hp["value"] = max(0, self.battle_state.pokemon1.current_hp)
        self.p2_hp["value"] = max(0, self.battle_state.pokemon2.current_hp)
        self.root.update_idletasks()

    def show_message(self, text):
        """Display a battle message."""
        self.message_label.config(text=text)
        self.root.update_idletasks()

    def update_turn(self, turn):
        """Update turn display."""
        self.turn_label.config(text=f"Turn {turn}")
        self.root.update_idletasks()

    def render_frame(self):
        """Call this each iteration in the game loop."""
        self.root.update()

    def close(self):
        self.root.destroy()
    
    def _on_resize(self, event):
        """Adjust layout dynamically when window is resized."""
        new_width = event.width
        new_height = event.height

        # Scale images proportionally
        scale_factor = new_width / 900  # baseline window width

        # Resize the Pokémon images dynamically
        front_resized = self.placeholder_img_front.resize(
            (int(200 * scale_factor), int(200 * scale_factor))
        )
        back_resized = self.placeholder_img_back.resize(
            (int(200 * scale_factor), int(200 * scale_factor))
        )

        self.placeholder_photo_front = ImageTk.PhotoImage(front_resized)
        self.placeholder_photo_back = ImageTk.PhotoImage(back_resized)

        self.p2_image.config(image=self.placeholder_photo_front)
        self.p1_image.config(image=self.placeholder_photo_back)

