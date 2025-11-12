from core.battle_state import BattleState
from core.pokemon import PokemonInstance

def evaluate_state(state: BattleState, player_is_pokemon1: bool = True) -> float:
    if player_is_pokemon1:
        player = state.pokemon1
        opponent = state.pokemon2
    else:
        player = state.pokemon2
        opponent = state.pokemon1

    if player.fainted() and opponent.fainted():
        return 0
    if player.fainted():
        return -1000
    if opponent.fainted():
        return 1000

    player_hp_ratio = player.current_hp / player.stats["hp"]
    opponent_hp_ratio = opponent.current_hp / opponent.stats["hp"]
    hp_factor = (player_hp_ratio - opponent_hp_ratio) * 100

    atk_diff = (player.get_stat("atk") - opponent.get_stat("atk")) / 2
    def_diff = (player.get_stat("def") - opponent.get_stat("def")) / 2
    spatk_diff = (player.get_stat("spatk") - opponent.get_stat("spatk")) / 4
    spdef_diff = (player.get_stat("spdef") - opponent.get_stat("spdef")) / 4

    spd_diff = (player.get_stat("speed") - opponent.get_stat("speed")) / 3

    weather_bonus = 0
    if getattr(state, "weather", None):
        if hasattr(player.ability, "weather"):
            if state.weather == player.ability.weather:
                weather_bonus += 10
        if hasattr(opponent.ability, "weather"):
            if state.weather == opponent.ability.weather:
                weather_bonus -= 10

    heuristic_score = hp_factor + atk_diff + def_diff + spd_diff + weather_bonus

    if hasattr(state, "field_effects"):
        if "reflect" in state.field_effects:
            heuristic_score += 5
        if "light_screen" in state.field_effects:
            heuristic_score += 5

    return heuristic_score
