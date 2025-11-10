import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from core.pokemon import PokemonInstance, PokemonSpecies
from core.move import Move

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pokémon Battle Menu")
        self.root.geometry("900x650")
        self.root.configure(bg="#d8e2f3")

        self.selected_team = None

        # Folder containing the 151 sprite pairs
        self.sprite_dir = "assets/sprites"

        # === Example Move Pool ===
        self.move_pool = [
            Move("Flamethrower", "Fire", 90, 100, "special"),
            Move("Hydro Pump", "Water", 110, 80, "special"),
            Move("Thunderbolt", "Electric", 90, 100, "special"),
            Move("Leaf Blade", "Grass", 90, 100, "physical"),
            Move("Rock Slide", "Rock", 75, 90, "physical"),
            Move("Ice Beam", "Ice", 90, 100, "special"),
        ]

        # === Load species dynamically ===
        self.species_pool = self._load_species_from_sprites()
        print(f"[INFO] Loaded {len(self.species_pool)} Pokémon species.")

    # --------------------------------------------------------
    # 🧩 Load Pokémon from sprite folder
    # --------------------------------------------------------
    def _load_species_from_sprites(self):
        if not os.path.exists(self.sprite_dir):
            print(f"[ERROR] Sprite directory '{self.sprite_dir}' not found.")
            return []

        files = [f for f in os.listdir(self.sprite_dir) if f.endswith(".png")]
        species_dict = {}

        for f in files:
            # Expected format: 001_Bulbasaur_b2w2_1.png
            parts = f.split("_")
            if len(parts) < 4:
                continue

            poke_name = parts[1]
            num_part = parts[-1].replace(".png", "")
            full_path = os.path.join(self.sprite_dir, f)

            # Match 1 ↔ 2 as front ↔ back
            if num_part == "1":
                species_dict.setdefault(poke_name, {})["front"] = full_path
            elif num_part == "2":
                species_dict.setdefault(poke_name, {})["back"] = full_path

        species_pool = []
        for name, sprites in species_dict.items():
            if "front" in sprites and "back" in sprites:
                stats = {"hp": 80, "atk": 80, "def": 80, "speed": 80, "spatk": 80, "spdef": 80}
                dummy_types = ["Normal"]
                species_pool.append(
                    PokemonSpecies(
                        name, dummy_types, stats, "Unknown", 1.0, 10.0,
                        f"A wild {name} appears!",
                        sprites["front"], sprites["back"]
                    )
                )

        return species_pool

    # --------------------------------------------------------
    # 🏁 Main entry
    # --------------------------------------------------------
    def run(self):
        self._show_start_screen()
        self.root.mainloop()
        return self.selected_team

    # --------------------------------------------------------
    # 🧢 Team Selection Screen
    # --------------------------------------------------------
    def _show_start_screen(self):
        self.clear_window()

        title = tk.Label(self.root, text="POKÉMON BATTLE", font=("Arial", 36, "bold"), bg="#d8e2f3")
        title.pack(pady=100)

        start_btn = tk.Button(
            self.root, text="Start Battle", font=("Arial", 16, "bold"),
            bg="#feca57", activebackground="#ff9f43",
            command=self._show_team_selection
        )
        start_btn.pack(pady=30)

        exit_btn = tk.Button(
            self.root, text="Exit", font=("Arial", 14),
            bg="#c8d6e5", command=self.root.destroy
        )
        exit_btn.pack(pady=10)

    def _show_team_selection(self):
        self.clear_window()

        title = tk.Label(self.root, text="Choose Your Team", font=("Arial", 28, "bold"), bg="#d8e2f3")
        title.pack(pady=20)

        if len(self.species_pool) < 3:
            tk.Label(self.root, text="Not enough Pokémon sprites loaded!", bg="#d8e2f3", fg="red").pack()
            return

        teams = [self._generate_team() for _ in range(3)]
        container = tk.Frame(self.root, bg="#d8e2f3")
        container.pack(pady=10)

        for i, team in enumerate(teams):
            frame = tk.Frame(container, bg="#ffffff", relief="raised", borderwidth=3)
            frame.grid(row=0, column=i, padx=20)

            tk.Label(frame, text=f"Team {i+1}", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=5)

            for mon in team:
                try:
                    img = Image.open(mon.species.front_sprite).resize((96, 96))
                    img = ImageTk.PhotoImage(img)
                    lbl = tk.Label(frame, image=img, bg="#ffffff")
                    lbl.image = img
                    lbl.pack()

                    # 🪄 Tooltip on hover
                    moves_text = "\n".join([m.name for m in mon.moves])
                    tooltip_text = f"{mon.species.name}\nMoves:\n{moves_text}"
                    self.create_tooltip(lbl, tooltip_text)

                except Exception as e:
                    lbl = tk.Label(frame, text=mon.species.name, font=("Arial", 12), bg="#ffffff")
                    lbl.pack(pady=3)
                    print(f"[WARN] Could not load sprite for {mon.species.name}: {e}")

                tk.Label(frame, text=", ".join(mon.species.types), bg="#ffffff", font=("Arial", 10)).pack()

            btn = tk.Button(
                frame, text="Select", font=("Arial", 12, "bold"),
                bg="#1dd1a1", command=lambda t=team: self._confirm_team(t)
            )
            btn.pack(pady=10)

    def _generate_team(self):
        if len(self.species_pool) < 3:
            print("[ERROR] Not enough Pokémon loaded! Check your sprite folder.")
            return []
        team_species = random.sample(self.species_pool, 3)
        team = []
        for s in team_species:
            moves = random.sample(self.move_pool, 2)
            team.append(PokemonInstance(s, level=random.randint(40, 55), moves=moves))
        return team

    def _confirm_team(self, team):
        self.selected_team = team
        self.root.destroy()

    def get_random_team(self):
        return self._generate_team()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --------------------------------------------------------
    # 💬 Tooltip (hover info)
    # --------------------------------------------------------
    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.withdraw()
        tooltip_label = tk.Label(
            tooltip, text=text, bg="#333", fg="white",
            font=("Arial", 10), justify="left", relief="solid", borderwidth=1, padx=5, pady=3
        )
        tooltip_label.pack()

        def enter(event):
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

