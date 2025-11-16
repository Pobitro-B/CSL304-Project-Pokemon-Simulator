import random
import time
from typing import Optional
from core.battle_state import BattleState
from core.move import Move
from core.pokemon import PokemonInstance, PokemonSpecies
from engine.action import Action, ActionType
from engine.renderer import GUIRenderer
from ai.minimax_agent import minimax
from copy import deepcopy


class BattleLoop:
    """Controls the main game flow — integrates logic with GUI rendering."""

    def __init__(self, battle_state: BattleState, renderer: Optional[GUIRenderer] = None):
        self.battle_state = battle_state
        self.renderer = renderer
        self.delay = 1.2  # seconds between updates for readability

    # ---------------------------------------------------
    # ACTION CHOICES
    # ---------------------------------------------------
    def choose_ai_action(self, ai_pokemon: PokemonInstance) -> Action:
        """AI chooses the best move using minimax instead of random."""
        if self.renderer:
            self.renderer.show_message(f"AI ({ai_pokemon.species.name}) is analyzing...")
            self.renderer.render_frame()
        time.sleep(0.8)

        # Perform minimax search
        try:
            _, best_move = minimax(
                deepcopy(self.battle_state),
                depth=2,                    # can tune for difficulty/speed
                alpha=float("-inf"),
                beta=float("inf"),
                maximizing_player=True,
                player_is_pokemon1=False    # since AI is usually player2
            )
        except Exception as e:
            print(f"Minimax failed: {e}, choosing move randomly")
            best_move = None

        # Fallback if minimax fails or returns None
        if not best_move:
            best_move = random.choice(ai_pokemon.moves)
        best_move = next((m for m in ai_pokemon.moves if m.name == best_move.name), best_move)
        return Action(ActionType.MOVE, ai_pokemon, target=None, move=best_move)


    def choose_player_action(self, player_pokemon: PokemonInstance) -> Action:
        """Waits for the player to pick a move in the GUI."""
        move = self.renderer.wait_for_move()
        return Action(ActionType.MOVE, player_pokemon, target=None, move=move)



    # ---------------------------------------------------
    # TURN EXECUTION
    # ---------------------------------------------------
    def simulate_turn(self, action1: Action, action2: Action):
        """Simulates one turn using the chosen Actions."""
        order = self.battle_state.get_turn_order()

        self.renderer.update_turn(self.battle_state.turn)
        self.renderer.show_message("The battle continues...")
        self.renderer.render_frame()

        time.sleep(0.5)

        for pokemon in order:
            if pokemon.fainted():
                continue

            action = action1 if action1.actor == pokemon else action2
            defender = (
                self.battle_state.ai_active
                if pokemon == self.battle_state.player_active
                else self.battle_state.player_active
            )

            if defender.fainted():
                break

            move = action.move
            self.renderer.show_message(f"{pokemon.species.name} used {move.name}!")
            self.renderer.render_frame()
            time.sleep(self.delay)

            # 🚨 FIX 1 — get both damage + multiplier
            damage, effectiveness = pokemon.attack(move, defender, self.battle_state)

            # 🚨 FIX 2 — remove the second damage application!
            # defender.take_damage(move, damage)  <-- delete this

            # defender.take_damage will already be called *inside* pokemon.attack()

            self.renderer.update_hp()

            self.renderer.show_message(f"It dealt {int(damage)} damage!")
            self.renderer.render_frame()
            time.sleep(0.6)

            # 🚨 FIX 3 — call effectiveness description
            from core.type_effectiveness import describe_effectiveness
            eff_text = describe_effectiveness(effectiveness)
            if eff_text:
                self.renderer.show_message(eff_text)
                self.renderer.render_frame()
                time.sleep(0.7)

            if defender.fainted():
                self.renderer.show_message(f"{defender.species.name} fainted!")
                self.renderer.update_hp()
                
                self.battle_state.handle_faint(defender)
                self.renderer._create_move_buttons()


                # If no Pokémon remain, end battle
                if self.battle_state.is_battle_over():
                    return

                # If someone was switched in, refresh HP bar
                self.renderer.update_hp()
                break


        self.battle_state.next_turn()

    # ---------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------
    def run(self):
        """Main battle loop."""
        player_pokemon = self.battle_state.player_active
        ai_pokemon = self.battle_state.ai_active

        while not self.battle_state.is_battle_over():
            self.renderer.update_hp()

            # Refresh active Pokémon each turn (important after faint/switch)
            player_pokemon = self.battle_state.player_active
            ai_pokemon = self.battle_state.ai_active

            player_action = self.choose_player_action(player_pokemon)
            ai_action = self.choose_ai_action(ai_pokemon)

            self.simulate_turn(player_action, ai_action)

        # End of Battle
        self.end_battle()

    # ---------------------------------------------------
    # END GAME DISPLAY
    # ---------------------------------------------------
    def end_battle(self):
        player_lost = self.battle_state.all_fainted(self.battle_state.player_team)
        ai_lost = self.battle_state.all_fainted(self.battle_state.ai_team)

        if player_lost and ai_lost:
            message = "Both teams are wiped out! It's a draw!"
        elif player_lost:
            message = "AI wins the battle!"
        else:
            message = "You win the battle!"


        self.renderer.show_message(message)
        self.renderer.render_frame()
        time.sleep(2)
        self.renderer.close()
