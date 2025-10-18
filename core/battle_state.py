# core/battle_state.py

from typing import Optional, List
from core.pokemon import PokemonInstance
from core.move import Move

class BattleState:
    """
    Holds the current state of a Pokémon battle.
    Tracks weather, turn order, field effects, and player Pokémon.
    """

    def __init__(self, pokemon1: PokemonInstance, pokemon2: PokemonInstance):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.turn = 1
        self.weather: Optional[str] = None  # e.g. "sunny", "rain", "sandstorm"
        self.field_effects = {}             # spikes, terrain, screens, etc.
        self.active_pokemon = [pokemon1, pokemon2]
        self.last_move: Optional[Move] = None

    # --------------------------
    # 🌦 Weather / Field Handling
    # --------------------------
    def set_weather(self, weather: Optional[str]):
        """Change weather and notify both Pokémon abilities."""
        self.weather = weather
        print(f"The weather changed to {weather or 'clear'}!")

        for p in self.active_pokemon:
            if hasattr(p.ability, "on_weather_change"):
                p.ability.on_weather_change(p, weather)

    # --------------------------
    # ⚔️ Turn Handling
    # --------------------------
    def next_turn(self):
        """Increment turn counter and apply end-of-turn effects."""
        print(f"\n--- Turn {self.turn} ends ---")
        for p in self.active_pokemon:
            if hasattr(p.ability, "on_end_turn"):
                p.ability.on_end_turn(p)
        self.turn += 1

    def get_turn_order(self) -> List[PokemonInstance]:
        """Return Pokémon in order of who moves first."""
        p1_speed = self.pokemon1.get_stat("speed")
        p2_speed = self.pokemon2.get_stat("speed")
        if p1_speed == p2_speed:
            # speed tie -> randomize
            import random
            return random.sample(self.active_pokemon, 2)
        return sorted(self.active_pokemon, key=lambda p: p.get_stat("speed"), reverse=True)

    # --------------------------
    # 💥 Damage + Move Execution
    # --------------------------
    def execute_move(self, attacker: PokemonInstance, defender: PokemonInstance, move: Move):
        """Handles damage, type effectiveness, and applying effects."""
        print(f"\n{attacker.species.name} used {move.name}!")

        damage = attacker.calculate_damage(move, defender, battle_state=self)
        defender.take_damage(damage)

        self.last_move = move
        print(f"It dealt {int(damage)} damage! {defender.species.name} has {defender.current_hp}/{defender.stats['hp']} HP left.")
        
        if defender.fainted():
            print(f"{defender.species.name} fainted!")

    # --------------------------
    # 🧠 Simulation Helper
    # --------------------------
    def simulate_turn(self, move1: Move, move2: Move):
        """Simulates a full turn (both players’ moves)."""
        order = self.get_turn_order()

        for pokemon in order:
            if pokemon.fainted():
                continue
            move = move1 if pokemon == self.pokemon1 else move2
            defender = self.pokemon2 if pokemon == self.pokemon1 else self.pokemon1
            self.execute_move(pokemon, defender, move)

        self.next_turn()
