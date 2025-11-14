from core.battle_state import BattleState
from core.pokemon import PokemonInstance

# ai/heuristics.py
from core.battle_state import BattleState
from core.move import Move
from core.type_effectiveness import get_effectiveness

def evaluate_state(state: BattleState, player_is_pokemon1: bool = True) -> float:
    """
    Heuristic for minimax. Uses:
      - HP difference (normalized)
      - best expected move effectiveness (weighted by power)
      - speed advantage
      - simple KO threshold awareness
    """
    if player_is_pokemon1:
        me = state.pokemon1
        opp = state.pokemon2
    else:
        me = state.pokemon2
        opp = state.pokemon1

    # Terminal handling
    if me.fainted() and opp.fainted():
        return 0.0
    if me.fainted():
        return -1000.0
    if opp.fainted():
        return 1000.0

    # --- 1) HP advantage (primary) ---
    my_hp_ratio = (me.current_hp / me.stats["hp"]) if me.stats.get("hp", 1) else 0.0
    opp_hp_ratio = (opp.current_hp / opp.stats["hp"]) if opp.stats.get("hp", 1) else 0.0
    hp_score = (my_hp_ratio - opp_hp_ratio) * 120.0

    # --- 2) Best expected move effectiveness (weighted by power) ---
    def best_expected_multiplier(attacker, defender):
        best = 0.0
        for m in getattr(attacker, "moves", []) or []:
            mt = getattr(m, "move_type", None)
            if not mt:
                continue
            # use get_effectiveness(attack_type, defender_types)
            try:
                eff = get_effectiveness(mt, getattr(defender.species, "types", getattr(defender, "types", [])))
            except Exception:
                eff = 1.0
            # weight by power (status moves get baseline 1.0)
            power = float(getattr(m, "power", 40) or 40)
            score = eff * (power / 100.0)   # normalized power contribution
            if score > best:
                best = score
        return best if best > 0.0 else 1.0

    my_best = best_expected_multiplier(me, opp)
    opp_best = best_expected_multiplier(opp, me)
    type_score = (my_best - opp_best) * 30.0   # tuned multiplier

    # --- 3) Speed advantage (who likely moves first) ---
    speed_score = 8.0 if me.get_stat("speed") > opp.get_stat("speed") else -8.0

    # --- 4) KO threshold (very small boosters to prefer finishing moves) ---
    ko_score = 0.0
    # Estimate roughly whether any of my moves could KO opp this turn (very rough)
    for m in getattr(me, "moves", []) or []:
        power = float(getattr(m, "power", 40) or 40)
        # rough expected damage proxy = power * (me.atk/opp.def) * effectiveness
        atk = me.get_stat("atk") if getattr(m, "category", "physical") == "physical" else me.get_stat("spatk")
        defe = opp.get_stat("def") if getattr(m, "category", "physical") == "physical" else opp.get_stat("spdef")
        try:
            eff = get_effectiveness(getattr(m, "move_type", ""), getattr(opp.species, "types", getattr(opp, "types", [])))
        except Exception:
            eff = 1.0
        est = (power * (atk / max(1.0, defe)) * eff) / 50.0  # very rough scaling
        if est >= opp.current_hp * 0.9:
            ko_score += 18.0  # strong preference to take an almost-certain KO
        elif est >= opp.current_hp * 0.5:
            ko_score += 6.0

    # Opponent potential to KO you (penalize)
    for m in getattr(opp, "moves", []) or []:
        power = float(getattr(m, "power", 40) or 40)
        atk = opp.get_stat("atk") if getattr(m, "category", "physical") == "physical" else opp.get_stat("spatk")
        defe = me.get_stat("def") if getattr(m, "category", "physical") == "physical" else me.get_stat("spdef")
        try:
            eff = get_effectiveness(getattr(m, "move_type", ""), getattr(me.species, "types", getattr(me, "types", [])))
        except Exception:
            eff = 1.0
        est = (power * (atk / max(1.0, defe)) * eff) / 50.0
        if est >= me.current_hp * 0.9:
            ko_score -= 20.0
        elif est >= me.current_hp * 0.5:
            ko_score -= 7.0

    # --- 5) Compose final heuristic ---
    score = hp_score + type_score + speed_score + ko_score

    # small normalization: keep values reasonable
    return float(score)
