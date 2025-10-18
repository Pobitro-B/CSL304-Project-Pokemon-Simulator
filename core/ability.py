# core/ability.py
# Load data dynamically
import json
with open("data/abilities.json", "r") as f:
    ABILITY_DATA = json.load(f)
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from core.pokemon import PokemonInstance
    from core.move import Move


class Ability:
    """Base class for Pokémon abilities.
    Abilities modify rules or events during battle.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    # --- Hooks: called automatically during battle events ---

    def on_damage_received(self, pokemon: "PokemonInstance", move: "Move", damage: float) -> float:
        """Called when the Pokémon is about to take damage.
        You can modify or negate it."""
        return damage

    def on_damage_dealt(self, pokemon: "PokemonInstance", move: "Move", damage: float) -> float:
        """Called when this Pokémon deals damage."""
        return damage

    def on_type_immunity(self, pokemon: "PokemonInstance", move_type: str) -> bool:
        """Return True if Pokémon is immune to a move type (e.g., Levitate vs Ground)."""
        return False

    def on_stat_calculation(self, pokemon: "PokemonInstance", stat_name: str, value: float) -> float:
        """Modify base stat (e.g., Huge Power doubles Attack)."""
        return value

    def on_weather_change(self, pokemon: "PokemonInstance", weather: Optional[str]):
        """Optional: react to weather changes."""
        pass

    def on_end_turn(self, pokemon: "PokemonInstance"):
        """Triggered at the end of each turn."""
        pass

# ----------------------------------------------------
# ⚡ Ability Type Classes
# ----------------------------------------------------

class ImmunityAbility(Ability):
    def __init__(self, name, immunity_type, description=""):
        super().__init__(name, description)
        self.immunity_type = immunity_type
    def on_type_immunity(self, pokemon, move_type):
        return move_type.lower() == self.immunity_type.lower()


class StatModifierAbility(Ability):
    def __init__(self, name, stat_target, multiplier, description=""):
        super().__init__(name, description)
        self.stat_target = stat_target.lower()
        self.multiplier = multiplier
    def on_stat_calculation(self, pokemon, stat_name, value):
        if stat_name.lower() == self.stat_target:
            return value * self.multiplier
        return value


class HealOnHitAbility(Ability):
    def __init__(self, name, trigger_type, heal_percent, description=""):
        super().__init__(name, description)
        self.trigger_type = trigger_type.lower()
        self.heal_percent = heal_percent
    def on_damage_received(self, pokemon, move, damage):
        if move.move_type.lower() == self.trigger_type:
            heal = pokemon.max_hp * self.heal_percent
            pokemon.current_hp = min(pokemon.max_hp, pokemon.current_hp + heal)
            print(f"{pokemon.name} healed for {int(heal)} HP due to {self.name}!")
            return 0
        return damage


class EntryDebuffAbility(Ability):
    def __init__(self, name, target_stat, change, description=""):
        super().__init__(name, description)
        self.target_stat = target_stat.lower()
        self.change = change
    def on_battle_entry(self, pokemon, opponent):
        opponent.modify_stat_stage(self.target_stat, self.change)
        print(f"{opponent.name}'s {self.target_stat} fell due to {pokemon.name}'s {self.name}!")


class WeatherBoostAbility(Ability):
    def __init__(self, name, weather, stat_target, multiplier, description=""):
        super().__init__(name, description)
        self.weather = weather.lower()
        self.stat_target = stat_target.lower()
        self.multiplier = multiplier
    def on_stat_calculation(self, pokemon, stat_name, value):
        if pokemon.battle_weather == self.weather and stat_name.lower() == self.stat_target:
            return value * self.multiplier
        return value


# ----------------------------------------------------
# 🧠 Factory Loader
# ----------------------------------------------------

def load_ability(name: str) -> Ability:
    """Return an ability instance based on JSON data."""
    data = ABILITY_DATA.get(name)
    if not data:
        return Ability(name, "No effect.")

    etype = data["effect_type"]

    if etype == "immunity":
        return ImmunityAbility(name, data["immunity_type"], data["description"])
    elif etype == "stat_modifier":
        return StatModifierAbility(name, data["stat_target"], data["multiplier"], data["description"])
    elif etype == "heal_on_hit":
        return HealOnHitAbility(name, data["trigger_type"], data["heal_percent"], data["description"])
    elif etype == "entry_debuff":
        return EntryDebuffAbility(name, data["target_stat"], data["change"], data["description"])
    elif etype == "weather_boost":
        return WeatherBoostAbility(name, data["weather"], data["stat_target"], data["multiplier"], data["description"])

    return Ability(name, data.get("description", ""))