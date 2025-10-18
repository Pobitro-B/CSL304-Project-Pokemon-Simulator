# core/pokemon.py

from typing import List, Dict, Optional
from .move import Move
from .ability import Ability, load_ability
from .type_effectiveness import get_effectiveness

class PokemonSpecies:
    """
    Represents a Pokémon species template.
    Holds all static properties that don't change between individual Pokémon.
    """
    def __init__(self, name: str, types: List[str], base_stats: Dict[str, int],
                 ability: Ability, height_m: float, weight_kg: float,
                 pokedex_entry: str, front_sprite: str, back_sprite: str):
        self.name = name
        self.types = types  # e.g., ['fire', 'flying']
        self.base_stats = base_stats  # e.g., {'hp': 78, 'atk': 84, ...}
        self.ability = ability
        self.height_m = height_m
        self.weight_kg = weight_kg
        self.pokedex_entry = pokedex_entry
        self.front_sprite = front_sprite
        self.back_sprite = back_sprite

    def __repr__(self):
        return f"<PokemonSpecies: {self.name} ({'/'.join(self.types)})>"


class PokemonInstance:
    """
    Represents an individual Pokémon in a battle.
    Includes types, stats, moves, and ability.
    """

    def __init__(
        self,
        species: "PokemonSpecies",
        level: int = 50,
        moves: Optional[List[Move]] = None,
        ability_name: Optional[str] = None,
    ):
        self.species = species
        self.name = species.name
        self.types = species.types
        self.level = level
        self.moves = moves or []
        self.base_stats = species.base_stats
        self.stats = self.calculate_stats(level)
        self.max_hp = self.stats["hp"]
        self.current_hp = self.max_hp
        self.status = None  # e.g., burn, paralysis
        self.stat_stages = {s: 0 for s in ["atk", "def", "spatk", "spdef", "speed"]}
        
        # 🧠 Ability System
        self.ability: Ability = load_ability(ability_name or species.default_ability)

    # -------------------------------------------------------
    # 🧮 Stat Handling
    # -------------------------------------------------------
    def calculate_stats(self, level: int) -> Dict[str, int]:
        """Compute level-scaled stats from base stats (no IVs/EVs yet)."""
        b = self.base_stats
        return {
            "hp": int(((2 * b["hp"] * level) / 100) + level + 10),
            "atk": int(((2 * b["atk"] * level) / 100) + 5),
            "def": int(((2 * b["def"] * level) / 100) + 5),
            "spatk": int(((2 * b["spatk"] * level) / 100) + 5),
            "spdef": int(((2 * b["spdef"] * level) / 100) + 5),
            "speed": int(((2 * b["speed"] * level) / 100) + 5),
        }

    def get_stat(self, stat_name: str) -> float:
        """Return the Pokémon's modified stat value after stages and ability."""
        base_val = self.stats[stat_name]
        stage = self.stat_stages.get(stat_name, 0)

        # Apply stage multiplier (simplified)
        if stage > 0:
            base_val *= (2 + stage) / 2
        elif stage < 0:
            base_val *= 2 / (2 - stage)

        # Ability stat modification
        base_val = self.ability.on_stat_calculation(self, stat_name, base_val)
        return base_val

    def modify_stat_stage(self, stat_name: str, change: int):
        """Change a stat stage (bounded between -6 and +6)."""
        old = self.stat_stages[stat_name]
        new = max(-6, min(6, old + change))
        self.stat_stages[stat_name] = new
        delta = "rose" if change > 0 else "fell"
        print(f"{self.name}'s {stat_name} {delta} to stage {new}!")

    # -------------------------------------------------------
    # ⚔️ Battle Actions
    # -------------------------------------------------------
    def take_damage(self, move: Move, damage: float):
        """Handle receiving damage, considering immunities and abilities."""
        if self.ability.on_type_immunity(self, move.move_type):
            print(f"{self.name} is immune to {move.move_type}-type moves due to {self.ability.name}!")
            return 0

        damage = self.ability.on_damage_received(self, move, damage)
        self.current_hp = max(0, self.current_hp - damage)

        if self.fainted():
            print(f"{self.name} fainted!")
        return damage

    def attack(self, move: Move, target: "PokemonInstance"):
        """Perform a move against the opponent Pokémon."""
        if move not in self.moves:
            raise ValueError(f"{self.name} doesn't know {move.name}!")

        # Type multiplier (handles dual-types, STAB, etc.)
        effectiveness = get_effectiveness( move.move_type, target.types, defender_ability=target.ability)

        # Calculate damage using Move’s internal formula
        damage = move.calculate_damage(self, target, effectiveness)

        # Apply ability-based modifications
        damage = self.ability.on_damage_dealt(self, move, damage)

        # Deal damage
        dealt = target.take_damage(move, damage)

        print(f"{self.name} used {move.name}! It dealt {int(dealt)} damage.")
        return dealt

    # -------------------------------------------------------
    # ❤️ HP / Status
    # -------------------------------------------------------
    def heal(self, amount: float):
        """Restore HP up to the max limit."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        print(f"{self.name} healed for {int(amount)} HP.")

    def fainted(self) -> bool:
        return self.current_hp <= 0

    # -------------------------------------------------------
    # 🪶 Utility
    # -------------------------------------------------------
    def on_battle_entry(self, opponent: "PokemonInstance"):
        """Trigger entry effects like Intimidate."""
        if hasattr(self.ability, "on_battle_entry"):
            self.ability.on_battle_entry(self, opponent)

    def __repr__(self):
        return f"<{self.name} Lv{self.level} HP:{int(self.current_hp)}/{self.max_hp} ({self.ability.name})>"