# core/type_effectiveness.py

# --- Type Effectiveness Chart ---
# Based on the standard Pokémon chart.
# Each dict entry shows effectiveness multipliers (2x, 0.5x, 0x) for attacking type.

TYPE_CHART = {
    "normal":  {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
    "fire":    {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2,
                "rock": 0.5, "dragon": 0.5, "steel": 2},
    "water":   {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "electric":{"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
    "grass":   {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2,
                "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "ice":     {"fire": 0.5, "water": 0.5, "grass": 2, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
    "fighting":{"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5,
                "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5},
    "poison":  {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2},
    "ground":  {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
    "flying":  {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug":     {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5,
                "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5, "fairy": 0.5},
    "rock":    {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
    "ghost":   {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "dragon":  {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark":    {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
    "steel":   {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "fairy": 2, "steel": 0.5},
    "fairy":   {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5},
}


def get_effectiveness(attack_type: str, defender_types: list[str], defender_ability=None) -> float:
    """
    Returns total type effectiveness multiplier.
    Handles:
    - Dual types (x4, x0.25, etc.)
    - Type immunities (0x)
    - Ability-based immunities (like Levitate)
    """
    attack_type = attack_type.lower()
    multiplier = 1.0

    if attack_type not in TYPE_CHART:
        return 1.0  # Unknown type fallback

    for d_type in defender_types:
        d_type = d_type.lower()
        effectiveness = TYPE_CHART.get(attack_type, {}).get(d_type, 1.0)
        multiplier *= effectiveness
    '''
    debug
    # --- Ability-based immunities ---
    if defender_ability:
        immunity_name = defender_ability.name.lower()
        if immunity_name == "levitate" and attack_type == "ground":
            return 0.0
        if immunity_name == "flash fire" and attack_type == "fire":
            return 0.0
        if immunity_name == "water absorb" and attack_type == "water":
            return 0.0
        if immunity_name == "volt absorb" and attack_type == "electric":
            return 0.0
        if immunity_name == "sap sipper" and attack_type == "grass":
            return 0.0
    '''
    return multiplier


def describe_effectiveness(multiplier: float) -> str:
    """Returns human-friendly description."""
    if multiplier == 0:
        return "It had no effect..."
    elif multiplier >= 4:
        return "It's *super* effective!"
    elif multiplier > 1:
        return "It's super effective!"
    elif multiplier < 1 and multiplier > 0:
        return "It's not very effective..."
    else:
        return ""
    
print(describe_effectiveness(0))
