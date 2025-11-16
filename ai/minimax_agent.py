from copy import deepcopy
from core.battle_state import BattleState
from core.move import Move
from ai.heuristics import evaluate_state

def _simulate_two_moves(state, move_a, move_b):
    order = state.get_turn_order()
    for attacker in order:
        if attacker.fainted():
            continue

        if attacker is state.player_active:
            move = move_a
            defender = state.ai_active
        else:
            move = move_b
            defender = state.player_active

        if move is None:
            continue

        try:
            damage = move.calculate_damage(attacker, defender, state)
        except TypeError:
            try:
                damage = move.calculate_damage(attacker, defender)
            except TypeError:
                damage = 1

        try:
            defender.take_damage(move, damage)
        except TypeError:
            try:
                defender.take_damage(damage)
            except Exception:
                pass

def minimax(state, depth, alpha, beta, maximizing_player, player_is_pokemon1=True):
    if depth == 0 or state.player_active.fainted() or state.ai_active.fainted():
        score = evaluate_state(state, player_is_pokemon1)
        return score, None

    if maximizing_player:
        our_pokemon = state.player_active if player_is_pokemon1 else state.ai_active
        opp_pokemon = state.ai_active if player_is_pokemon1 else state.player_active
    else:
        our_pokemon = state.ai_active if player_is_pokemon1 else state.player_active
        opp_pokemon = state.player_active if player_is_pokemon1 else state.ai_active

    best_move = None

    if maximizing_player:
        max_eval = float("-inf")
        for our_move in our_pokemon.moves if our_pokemon.moves else [None]:
            opp_moves = opp_pokemon.moves if opp_pokemon.moves else [None]

            for opp_move in opp_moves:
                state_copy = deepcopy(state)
                if player_is_pokemon1:
                    move1 = our_move if maximizing_player else opp_move
                    move2 = opp_move if maximizing_player else our_move
                else:
                    move1 = opp_move if maximizing_player else our_move
                    move2 = our_move if maximizing_player else opp_move

                _simulate_two_moves(state_copy, move1, move2)
                eval_score, _ = minimax(state_copy, depth - 1, alpha, beta, False, player_is_pokemon1)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = our_move

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for opp_move in our_pokemon.moves if our_pokemon.moves else [None]:
            our_responses = opp_pokemon.moves if opp_pokemon.moves else [None]
            for our_resp in our_responses:
                state_copy = deepcopy(state)
                if player_is_pokemon1:
                    move1 = our_resp
                    move2 = opp_move
                else:
                    move1 = opp_move
                    move2 = our_resp
                _simulate_two_moves(state_copy, move1, move2)
                eval_score, _ = minimax(state_copy, depth - 1, alpha, beta, True, player_is_pokemon1)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = opp_move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            if beta <= alpha:
                break
        return min_eval, best_move
