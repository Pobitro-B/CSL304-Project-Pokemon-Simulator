# core/battle_state.py

from typing import Optional, List, Dict
from core.pokemon import PokemonInstance
from core.move import Move
import random


class BattleState:
    """
    Represents the state of an ongoing Pokémon battle.
    Tracks weather, field effects, active Pokémon, and turn progression.
    """

    def __init__(self, player_team: List[PokemonInstance], ai_team: List[PokemonInstance]):
        self.player_team = player_team
        self.ai_team = ai_team

        self.player_active = player_team[0]
        self.ai_active = ai_team[0]

        self.player_idx = 0
        self.ai_idx = 0

        self.turn = 1

        # Environmental factors
        self.weather: Optional[str] = None   # e.g. "sunny", "rain", "sandstorm"
        self.field_effects: Dict[str, any] = {}  # e.g. {"spikes": 1, "reflect": True}

        # Meta info
        self.active_pokemon = lambda: [self.player_active, self.ai_active]
        self.last_move: Optional[Move] = None

    # --------------------------------------------------------
    # 🌦 WEATHER HANDLING
    # --------------------------------------------------------
    def set_weather(self, weather: Optional[str]):
        """Set or clear weather and trigger related abilities."""
        prev_weather = self.weather
        self.weather = weather

        if weather != prev_weather:
            print(f"The weather changed to {weather or 'clear skies'}!")

            # Notify all Pokémon about the weather change
            for p in self.active_pokemon():
                if hasattr(p.ability, "on_weather_change"):
                    p.ability.on_weather_change(p, weather)

    # --------------------------------------------------------
    # ⚔️ TURN MANAGEMENT
    # --------------------------------------------------------
    def start_turn(self):
        """Prepare start-of-turn triggers (like abilities)."""
        print(f"\n--- Turn {self.turn} begins ---")
        for p in self.active_pokemon():
            if hasattr(p.ability, "on_turn_start"):
                p.ability.on_turn_start(p, self)

    def next_turn(self):
        """End the turn, handle end-of-turn effects, increment counter."""
        print(f"--- Turn {self.turn} ends ---\n")
        for p in self.active_pokemon():
            if hasattr(p.ability, "on_end_turn"):
                p.ability.on_end_turn(p, self)
        self.turn += 1

    def get_turn_order(self) -> List[PokemonInstance]:
        """Determine turn order based on speed (randomized tie)."""
        p1_speed = self.player_active.get_stat("speed")
        p2_speed = self.ai_active.get_stat("speed")

        if p1_speed == p2_speed:
            return random.sample(self.active_pokemon(), 2)
        return sorted(self.active_pokemon(), key=lambda p: p.get_stat("speed"), reverse=True)

    # --------------------------------------------------------
    # 💥 MOVE EXECUTION
    # --------------------------------------------------------
    def execute_move(self, attacker: PokemonInstance, defender: PokemonInstance, move: Move):
        """Execute a single move with type effectiveness and ability hooks."""
        if attacker.fainted():
            print(f"{attacker.species.name} has fainted and cannot move!")
            return

        print(f"\n{attacker.species.name} used {move.name}!")

        # Check for ability-based move immunity
        if hasattr(defender.ability, "is_move_immune") and defender.ability.is_move_immune(move):
            print(f"It doesn’t affect {defender.species.name} due to its ability!")
            return

        self.last_move = move
        attacker.attack(move, defender, self)
        # After damage, check if defender fainted
        if defender.fainted():
            team = self.player_team if defender is self.player_active else self.ai_team
            next_mon = self._next_available(team)

            if next_mon:
                # Auto-switch
                if defender is self.player_active:
                    self.player_active = next_mon
                else:
                    self.ai_active = next_mon

                print(f"{defender.species.name} fainted! {next_mon.species.name} enters the battle!")
            else:
                print(f"{defender.species.name} fainted! No Pokémon left on that side!")



    # --------------------------------------------------------
    # 🧠 TURN SIMULATION
    # --------------------------------------------------------
    def simulate_turn(self, move1: Move, move2: Move):
        """Simulate both Pokémon using one move each."""
        self.start_turn()
        order = self.get_turn_order()

        for pokemon in order:
            if pokemon.fainted():
                continue

            if pokemon == self.player_active:
                move = move1
                defender = self.ai_active
            else:
                move = move2
                defender = self.player_active


            self.execute_move(pokemon, defender, move)

        self.next_turn()

    def _next_available(self, team: List[PokemonInstance]):
        for mon in team:
            if not mon.fainted():
                return mon
        return None

    def switch(self, player: int, new_mon: PokemonInstance):
        if player == 1:
            self.player_active = new_mon
        else:
            self.ai_active = new_mon

        print(f"{new_mon.species.name} was sent out!")

    # ------------------------------------------------------
    #  Faint handling
    # ------------------------------------------------------
    def handle_faint(self, pokemon):
        """Called by game_loop when a Pokémon reaches 0 HP."""
        if pokemon == self.player_active:
            return self._player_fainted()
        else:
            return self._ai_fainted()

    # ------------------------------------------------------
    #  Player faint
    # ------------------------------------------------------
    def _player_fainted(self):
        self.player_active.current_hp = 0

        # check if any remain alive
        next_idx = self._find_next_alive(self.player_team, self.player_idx)
        if next_idx is None:
            return  # player team dead -> battle ends

        self.player_idx = next_idx
        self.player_active = self.player_team[next_idx]

    # ------------------------------------------------------
    #  AI faint
    # ------------------------------------------------------
    def _ai_fainted(self):
        self.ai_active.current_hp = 0

        next_idx = self._find_next_alive(self.ai_team, self.ai_idx)
        if next_idx is None:
            return

        self.ai_idx = next_idx
        self.ai_active = self.ai_team[next_idx]

    # ------------------------------------------------------
    #  Find next alive Pokémon
    # ------------------------------------------------------
    def _find_next_alive(self, team, start_idx=0):
        """Return index of next alive Pokémon after start_idx, or None."""
        for i in range(start_idx + 1, len(team)):
            if getattr(team[i], "current_hp", 0) > 0:
                return i
        return None

    # ------------------------------------------------------
    #  Is battle over?
    # ------------------------------------------------------
    def is_battle_over(self):
        player_alive = any(p.current_hp > 0 for p in self.player_team)
        ai_alive = any(p.current_hp > 0 for p in self.ai_team)

        return not (player_alive and ai_alive)

    # ------------------------------------------------------
    #  Winner
    # ------------------------------------------------------
    def get_winner(self):
        player_alive = any(p.current_hp > 0 for p in self.player_team)
        ai_alive = any(p.current_hp > 0 for p in self.ai_team)

        if player_alive and not ai_alive:
            return "player"
        if ai_alive and not player_alive:
            return "ai"
        return "tie"

    @property
    def pokemon1(self):
        return self.player_active

    @property
    def pokemon2(self):
        return self.ai_active

    def all_fainted(self, team):
        """Return True if every Pokémon in the team has fainted."""
        return all(p.current_hp <= 0 for p in team)
