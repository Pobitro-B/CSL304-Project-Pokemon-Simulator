import random
import time
from typing import Optional
from core.battle_state import BattleState
from core.move import Move
from core.pokemon import PokemonInstance, PokemonSpecies
from engine.action import Action, ActionType
from engine.renderer import GUIRenderer


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
        """Basic AI that randomly picks a move."""
        move = random.choice(ai_pokemon.moves)
        if self.renderer:
            self.renderer.show_message(f"AI ({ai_pokemon.species.name}) is thinking...")
            self.renderer.render_frame()
        time.sleep(0.8)
        return Action(ActionType.MOVE, ai_pokemon, target = None, move=move)

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
                self.battle_state.pokemon2
                if pokemon == self.battle_state.pokemon1
                else self.battle_state.pokemon1
            )

            if defender.fainted():
                break

            move = action.move
            self.renderer.show_message(f"{pokemon.species.name} used {move.name}!")
            self.renderer.render_frame()
            time.sleep(self.delay)

            # Damage logic
            damage = pokemon.attack(move, defender, self.battle_state)
            defender.take_damage(move, damage)

            self.renderer.update_hp()
            self.renderer.show_message(f"It dealt {int(damage)} damage!")
            self.renderer.render_frame()

            if defender.fainted():
                self.renderer.show_message(f"{defender.species.name} fainted!")
                self.renderer.update_hp()
                break

        self.battle_state.next_turn()

    # ---------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------
    def run(self):
        """Main battle loop."""
        player_pokemon = self.battle_state.pokemon1
        ai_pokemon = self.battle_state.pokemon2

        while not player_pokemon.fainted() and not ai_pokemon.fainted():
            self.renderer.update_hp()

            player_action = self.choose_player_action(player_pokemon)
            ai_action = self.choose_ai_action(ai_pokemon)

            self.simulate_turn(player_action, ai_action)

        # End of Battle
        self.end_battle()

    # ---------------------------------------------------
    # END GAME DISPLAY
    # ---------------------------------------------------
    def end_battle(self):
        p1 = self.battle_state.pokemon1
        p2 = self.battle_state.pokemon2

        if p1.fainted() and p2.fainted():
            message = "It's a double knockout! The battle ends in a draw!"
        elif p1.fainted():
            message = f"{p2.species.name} wins the battle!"
        else:
            message = f"{p1.species.name} wins the battle!"

        self.renderer.show_message(message)
        self.renderer.render_frame()
        time.sleep(2)
        self.renderer.close()
