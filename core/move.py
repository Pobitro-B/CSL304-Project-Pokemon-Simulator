# core/move.py
from core.type_effectiveness import get_effectiveness
from typing import Optional, Callable

class Move:
    """
    Represents a Pokémon move (attack, status, etc.)
    """
    def __init__(self, name: str, move_type: str, power: Optional[int],
                 accuracy: int, category: str,
                 pp: int = 10, priority: int = 0,
                 effect: Optional[Callable] = None,
                 effect_chance: Optional[float] = None,
                 description: str = ""):
        """
        Parameters:
        - name: str → Move name, e.g., "Flamethrower"
        - move_type: str → Pokémon type (e.g., 'fire', 'water', etc.)
        - power: int | None → Base power; None for status moves
        - accuracy: int → Chance (0–100)
        - category: 'physical' | 'special' | 'status'
        - pp: Power Points (max usage count)
        - priority: determines turn order (e.g., Quick Attack)
        - effect: optional callable that modifies state (e.g., burn chance)
        - effect_chance: chance of effect triggering
        - description: short flavor text
        """
        self.name = name
        self.move_type = move_type
        self.power = power
        self.accuracy = accuracy
        self.category = category
        self.pp = pp
        self.priority = priority
        self.effect = effect
        self.effect_chance = effect_chance
        self.description = description

    def use_move(self, attacker, defender, battle_state):
        """
        Core logic when a move is executed.
        Will later use type multipliers, ability effects, etc.
        """
        if self.pp <= 0:
            print(f"{attacker.species.name} tried to use {self.name}, but it's out of PP!")
            return

        self.pp -= 1  # Decrease move PP
        # For now, just print; later we’ll integrate type chart + crit logic
        print(f"{attacker.species.name} used {self.name}!")

        # Placeholder: compute basic damage if power-based
        if self.power:
            damage = self.calculate_damage(attacker, defender, battle_state)
            defender.take_damage(damage)

            print(f"It dealt {damage:.1f} damage!")
            if defender.fainted():
                print(f"{defender.species.name} fainted!")
        else:
            print(f"{self.name} had no direct damage effect.")

        # Handle possible secondary effect
        if self.effect and self.effect_chance:
            import random
            if random.random() < self.effect_chance:
                self.effect(attacker, defender, battle_state)

    def calculate_damage(self, attacker, defender, battle_state):
        """
        Basic damage formula — simplified version.
        Real Pokémon formula is much more complex.
        """
        level = attacker.level
        power = self.power or 0
        attack_stat = (attacker.stats["atk"]
                       if self.category == "physical" else attacker.stats["spatk"])
        defense_stat = (defender.stats["def"]
                        if self.category == "physical" else defender.stats["spdef"])

        # Simplified Pokémon damage formula
        base_damage = (((2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2

        # Apply STAB (Same Type Attack Bonus)
        stab = 1.5 if self.move_type in attacker.species.types else 1.0

        # Type effectiveness (we’ll link with type chart later)
        type_multiplier = get_effectiveness(self.move_type, defender.species.types, defender.species.ability)


        # Random factor (0.85–1.00)
        import random
        random_factor = random.uniform(0.85, 1.0)

        total_damage = base_damage * stab * type_multiplier * random_factor
        return max(1, int(total_damage))  # minimum 1 damage

    def __repr__(self):
        return f"<Move: {self.name} ({self.move_type}, {self.category}, {self.power})>"
