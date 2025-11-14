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

    def __init__(self, pokemon1: PokemonInstance, pokemon2: PokemonInstance):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.turn = 1

        # Environmental factors
        self.weather: Optional[str] = None   # e.g. "sunny", "rain", "sandstorm"
        self.field_effects: Dict[str, any] = {}  # e.g. {"spikes": 1, "reflect": True}

        # Meta info
        self.active_pokemon = [pokemon1, pokemon2]
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
            for p in self.active_pokemon:
                if hasattr(p.ability, "on_weather_change"):
                    p.ability.on_weather_change(p, weather)

    # --------------------------------------------------------
    # ⚔️ TURN MANAGEMENT
    # --------------------------------------------------------
    def start_turn(self):
        """Prepare start-of-turn triggers (like abilities)."""
        print(f"\n--- Turn {self.turn} begins ---")
        for p in self.active_pokemon:
            if hasattr(p.ability, "on_turn_start"):
                p.ability.on_turn_start(p, self)

    def next_turn(self):
        """End the turn, handle end-of-turn effects, increment counter."""
        print(f"--- Turn {self.turn} ends ---\n")
        for p in self.active_pokemon:
            if hasattr(p.ability, "on_end_turn"):
                p.ability.on_end_turn(p, self)
        self.turn += 1

    def get_turn_order(self) -> List[PokemonInstance]:
        """Determine turn order based on speed (randomized tie)."""
        p1_speed = self.pokemon1.get_stat("speed")
        p2_speed = self.pokemon2.get_stat("speed")

        if p1_speed == p2_speed:
            return random.sample(self.active_pokemon, 2)
        return sorted(self.active_pokemon, key=lambda p: p.get_stat("speed"), reverse=True)

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

            move = move1 if pokemon == self.pokemon1 else move2
            defender = self.pokemon2 if pokemon == self.pokemon1 else self.pokemon1

            self.execute_move(pokemon, defender, move)

        self.next_turn()
