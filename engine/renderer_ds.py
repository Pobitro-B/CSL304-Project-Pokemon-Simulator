# engine/renderer_ds.py
import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
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
    """
    DS-style battle renderer (responsive).

    Key fixes:
    - Force redraw on HP updates (update_hp calls _on_resize(force=True))
    - Remove stale canvas items by tags before drawing new ones
    - Adjust sprite / HP positions so player HP is visible and enemy counters don't overlap
    """

    def __init__(self, battle_state, bg_path="battle_bg.jpg"):
        self.battle_state = battle_state
        self.root = tk.Tk()
        self.root.title("Pokémon Battle (DS Mode)")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        # --- Load background (safe) ---
        if bg_path and os.path.exists(bg_path):
            self.bg_image = Image.open(bg_path).convert("RGBA")
        else:
            # fallback colored background
            self.bg_image = Image.new("RGBA", (900, 420), "#6aa0d6")
        self.bg_photo = None

        # --- Sprite sizing ---
        self.base_sprite_size = 300
        self.default_front_path = getattr(battle_state, "default_front", None)
        self.default_back_path = getattr(battle_state, "default_back", None)

        # keep PhotoImage refs here to avoid GC
        self._tk_images = {}

        # --- Canvas / UI ---
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg="#6aa0d6")
        self.canvas.pack(fill="both", expand=True)

        # bottom panel (message + moves)
        self.bottom_frame = tk.Frame(self.root, bg="#222831")
        self.bottom_frame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)

        # message label
        self.message_label = tk.Label(
            self.bottom_frame, text="", font=("Consolas", 13),
            bg="#2C2F33", fg="white", anchor="w", justify="left", padx=20
        )
        self.message_label.place(relx=0.02, rely=0.05, relwidth=0.96, relheight=0.25)

        # move grid
        self.move_frame = tk.Frame(self.bottom_frame, bg="#2C2F33")
        self.move_frame.place(relx=0.15, rely=0.35, relwidth=0.7, relheight=0.55)

        self.move_buttons = []
        self.selected_move = None

        # cancel button
        self.cancel_button = tk.Button(
            self.bottom_frame, text="CANCEL", font=("Arial", 11, "bold"),
            bg="#F8C8B8", activebackground="#F4978E", command=self._cancel_selection
        )
        self.cancel_button.place(relx=0.43, rely=0.93, anchor="s")

        # turn label (floating)
        self.turn_label = tk.Label(
            self.root, text="Turn 1", font=("Arial", 14, "bold"),
            bg="#FFFFFF", fg="black"
        )
        self.turn_label.place(relx=0.5, rely=0.03, anchor="n")

        # ensure teams exist
        self._ensure_teams()

        # create move buttons
        self._create_move_buttons()

        # bind resize
        self.root.bind("<Configure>", self._on_resize)

        # cache last size to avoid useless redraws
        self._last_canvas_size = (0, 0)

        # trigger first draw
        self.root.update()
        self._on_resize(force=True)

    # --------------------------
    # Team helpers
    # --------------------------
    def _ensure_teams(self):
        """Make sure player_team and enemy_team exist (1v1)."""
        # player
        if hasattr(self.battle_state, "pokemon1") and getattr(self.battle_state, "pokemon1"):
            self.player_team = [getattr(self.battle_state, "pokemon1")]
        elif hasattr(self.battle_state, "selected_team") and getattr(self.battle_state, "selected_team"):
            self.player_team = [getattr(self.battle_state, "selected_team")[0]]
        elif hasattr(self.battle_state, "player_team") and getattr(self.battle_state, "player_team"):
            self.player_team = [getattr(self.battle_state, "player_team")[0]]
        else:
            raise RuntimeError("No player Pokémon found in battle_state (expected pokemon1 or selected_team).")

        # enemy
        if hasattr(self.battle_state, "pokemon2") and getattr(self.battle_state, "pokemon2"):
            self.enemy_team = [getattr(self.battle_state, "pokemon2")]
        elif hasattr(self.battle_state, "enemy_pokemon") and getattr(self.battle_state, "enemy_pokemon"):
            self.enemy_team = [getattr(self.battle_state, "enemy_pokemon")]
        elif hasattr(self.battle_state, "enemy_team") and getattr(self.battle_state, "enemy_team"):
            self.enemy_team = [getattr(self.battle_state, "enemy_team")[0]]
        else:
            pool = getattr(self.battle_state, "species_pool", None) or getattr(self.battle_state, "available_species", None)
            if not pool:
                raise RuntimeError("No enemy Pokémon or pool found to generate one.")
            s = random.choice(pool)
            obj = type("SimplePI", (), {})()
            obj.species = s
            base_hp = int(getattr(s, "stats", {}).get("hp", 60))
            obj.max_hp = obj.current_hp = base_hp
            obj.level = 50
            obj.moves = getattr(s, "default_moves", [])[:4] or []
            self.enemy_team = [obj]

        self.player_active = 0
        self.enemy_active = 0

    def _get_active(self, which="player"):
        if which == "player":
            return self.player_team[self.player_active] if 0 <= self.player_active < len(self.player_team) else self.player_team[0]
        else:
            return self.enemy_team[self.enemy_active] if 0 <= self.enemy_active < len(self.enemy_team) else self.enemy_team[0]

    # --------------------------
    # Move buttons
    # --------------------------
    def _create_move_buttons(self):
        # destroy old
        for b in self.move_buttons:
            b.destroy()
        self.move_buttons.clear()

        player_active = self._get_active("player")
        moves = getattr(player_active, "moves", []) or []

        # configure grid
        for r in range(2):
            self.move_frame.grid_rowconfigure(r, weight=1)
        for c in range(2):
            self.move_frame.grid_columnconfigure(c, weight=1)

        for i in range(4):
            if i < len(moves):
                move = moves[i]
                color = TYPE_COLORS.get(getattr(move, "move_type", "default"), TYPE_COLORS["default"])
                text = f"{getattr(move, 'name', 'Move')}\nPP {getattr(move, 'pp', 10)}\n{getattr(move, 'move_type', '')}"
                cmd = (lambda m=moves[i]: self._select_move(m))
                state = tk.NORMAL
            else:
                color = "#555"
                text = "---\nPP --\n---"
                cmd = (lambda: None)
                state = tk.DISABLED

            btn = tk.Button(
                self.move_frame,
                text=text,
                font=("Arial", 11, "bold"),
                bg=color, fg="white",
                relief="raised",
                state=state,
                command=cmd
            )
            btn.grid(row=i // 2, column=i % 2, padx=12, pady=8, sticky="nsew")
            self.move_buttons.append(btn)

    # --------------------------
    # Events
    # --------------------------
    def _select_move(self, move):
        self.selected_move = move
        self.show_message(f"You selected {move.name}!", delay=0.5)

    def _cancel_selection(self):
        self.selected_move = None
        self.show_message("Move selection canceled.", delay=0.4)

    def wait_for_move(self):
        self.selected_move = None
        self._set_move_buttons_state(tk.NORMAL)
        self.show_message("Choose your move...")
        while self.selected_move is None:
            self.root.update()
            time.sleep(0.01)
        self._set_move_buttons_state(tk.DISABLED)
        return self.selected_move

    def _set_move_buttons_state(self, state):
        for btn in self.move_buttons:
            btn.config(state=state)

    # --------------------------
    # Rendering
    # --------------------------
    def _on_resize(self, event=None, force=False):
        """
        Redraw the main canvas. If force==True, redraw even when size hasn't changed (used by update_hp).
        """
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        if not force and (w, h) == self._last_canvas_size:
            return
        self._last_canvas_size = (w, h)

        # --- clear relevant tags to avoid duplicates ---
        # keep bottom_frame and widgets intact (they are normal widgets),
        # clear canvas-drawn things (bg, sprites, hp, remain)
        for tag in ("bg", "sprites", "hp", "hp_fill", "hp_text", "remain_player", "remain_enemy"):
            self.canvas.delete(tag)

        # redraw background scaled to top 70%
        bg_resized = self.bg_image.resize((w, int(h * 0.7)))
        self.bg_photo = ImageTk.PhotoImage(bg_resized)
        self._tk_images["bg"] = self.bg_photo
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo, tags="bg")

        # compute sprite size with margin to keep them visible over bottom panel
        scale_factor = min(w / 900, h / 650)
        size = max(120, int(self.base_sprite_size * scale_factor * 0.8))

        # get active pokémon
        player_active = self._get_active("player")
        enemy_active = self._get_active("enemy")

        # load image paths (safe)
        player_back_path = getattr(player_active.species, "back_sprite", None) or getattr(player_active.species, "back", None) or self.default_back_path
        enemy_front_path = getattr(enemy_active.species, "front_sprite", None) or getattr(enemy_active.species, "front", None) or self.default_front_path

        def load_image(path, default_color=(200, 200, 200, 255)):
            try:
                if path and os.path.exists(path):
                    im = Image.open(path).convert("RGBA")
                else:
                    im = Image.new("RGBA", (size, size), default_color)
                im = im.resize((size, size), Image.LANCZOS)
                return im
            except Exception:
                return Image.new("RGBA", (size, size), default_color)

        player_img = load_image(player_back_path)
        enemy_img = load_image(enemy_front_path)

        player_photo = ImageTk.PhotoImage(player_img)
        enemy_photo = ImageTk.PhotoImage(enemy_img)

        # store references so TK won't garbage collect
        self._tk_images["player"] = player_photo
        self._tk_images["enemy"] = enemy_photo

        # positions - adjusted so player is lower (HP visible) and enemy up/right
        player_x, player_y = int(w * 0.25), int(h * 0.62)
        enemy_x, enemy_y = int(w * 0.75), int(h * 0.28)

        # draw sprites
        self.canvas.create_image(player_x, player_y, image=player_photo, anchor="center", tags="sprites")
        self.canvas.create_image(enemy_x, enemy_y, image=enemy_photo, anchor="center", tags="sprites")

        # draw HP bars after sprites so they appear on top
        self._draw_hp_bar(player_x, player_y + size // 2 + 12, player_active, w, side="player")
        self._draw_hp_bar(enemy_x, enemy_y - size // 2 - 34, enemy_active, w, side="enemy")

        # draw remaining counters (player bottom-left above bottom panel, enemy top-right)
        self._draw_remaining_counter(w, h, side="player")
        self._draw_remaining_counter(w, h, side="enemy")

    def _draw_hp_bar(self, x, y, pokemon, canvas_width, side="player"):
        """
        Draw an HP bar at (x, y). Uses tags so we can clear it easily later.
        """
        bar_w = int(canvas_width * 0.28)
        bar_h = 18
        left = x - bar_w // 2
        right = x + bar_w // 2
        top = y
        bottom = y + bar_h

        # compute hp values
        current = getattr(pokemon, "current_hp", None)
        maximum = getattr(pokemon, "max_hp", None)
        if current is None or maximum is None:
            stats = getattr(getattr(pokemon, "species", None), "stats", {}) or {}
            maximum = stats.get("hp", 60)
            current = getattr(pokemon, "current_hp", maximum)

        # clamp numeric values
        try:
            current = float(current)
            maximum = float(maximum)
        except Exception:
            current = float(max(0, int(current or 0)))
            maximum = float(max(1, int(maximum or 1)))

        # background frame (outer)
        self.canvas.create_rectangle(left - 2, top - 2, right + 2, bottom + 2, fill="#222", outline="#000", tags="hp")
        # inner background
        self.canvas.create_rectangle(left, top, right, bottom, fill="#444", outline="#000", tags="hp")

        # fill width
        pct = max(0.0, min(1.0, (current / maximum) if maximum > 0 else 0.0))
        fill_w = int(bar_w * pct)
        fill_color = "#2ecc71" if pct > 0.5 else ("#f1c40f" if pct > 0.2 else "#e74c3c")
        if fill_w > 0:
            self.canvas.create_rectangle(left, top, left + fill_w, bottom, fill=fill_color, outline="", tags="hp_fill")

        # text overlay: name and hp (left aligned for player, right aligned for enemy)
        name = getattr(getattr(pokemon, "species", None), "name", "Pokémon")
        hp_text = f"{int(current)}/{int(maximum)} HP"
        anchor = "w" if side == "player" else "e"
        text_x = left + 6 if side == "player" else right - 6
        # background for text for readability
        self.canvas.create_rectangle(text_x - 6 if side == "player" else text_x - 220, top - 20, text_x + (bar_w if side == "player" else 6), top - 2, fill="#111", outline="", tags="hp")
        self.canvas.create_text(text_x, top - 11, text=f"{name}  {hp_text}", fill="white", anchor=anchor, font=("Arial", 11, "bold"), tags="hp_text")

    def _draw_remaining_counter(self, canvas_w, canvas_h, side="player"):
        """
        Draw a small pill with icons showing remaining pokémon count.
        Player's pill placed near bottom-left above the bottom panel.
        Enemy's pill placed near the top-right (but not overlapping HP).
        """
        team = self.player_team if side == "player" else self.enemy_team
        alive = sum(1 for p in team if getattr(p, "current_hp", getattr(p, "max_hp", 1)) > 0)
        total = len(team)
        size = 18
        spacing = 6

        if side == "player":
            # place above bottom UI panel on left
            y = int(canvas_h * 0.70) + 8
            x_start = int(canvas_w * 0.05)
        else:
            # place at top-right, but slightly lower than top edge to avoid hp bar overlap
            y = int(canvas_h * 0.06)
            x_start = int(canvas_w * 0.78)

        # background pill rectangle
        pill_w = max(80, total * (size + spacing) + 30)
        pill_h = size + 10
        pill_left = x_start
        if side == "enemy":
            pill_left = x_start
        pill_right = pill_left + pill_w

        tag = "remain_player" if side == "player" else "remain_enemy"
        self.canvas.create_rectangle(pill_left, y, pill_right, y + pill_h, fill="#111", outline="#000", tags=tag)

        # small circles for each slot
        for i in range(total):
            cx = pill_left + 12 + i * (size + spacing)
            cy = y + pill_h // 2
            fill = "#2ecc71" if i < alive else "#555"
            self.canvas.create_oval(cx, cy - size // 2, cx + size, cy + size // 2, fill=fill, outline="#000", tags=tag)

        # text count on right side of pill
        self.canvas.create_text(pill_right - 10, y + pill_h // 2, text=f"{alive}/{total}", fill="white", anchor="e", font=("Arial", 10, "bold"), tags=tag)

    # --------------------------
    # Updates callable from game logic
    # --------------------------
    def update_turn(self, turn):
        self.turn_label.config(text=f"Turn {turn}")
        self.root.update_idletasks()

    def update_hp(self):
        """
        Force a redraw of the canvas area to reflect new HP values.
        Uses _on_resize(force=True) so the canvas is redrawn even if window size hasn't changed.
        """
        self._on_resize(force=True)
        self.root.update_idletasks()

    def show_message(self, text, delay=0.9):
        self.message_label.config(text=text)
        self.root.update_idletasks()
        if delay and delay > 0:
            time.sleep(delay)

    def render_frame(self):
        self.root.update()

    def close(self):
        self.root.destroy()
