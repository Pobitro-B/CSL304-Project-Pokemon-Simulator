from engine.game_loop import BattleLoop
from engine.renderer_ds import GUIRendererDS
from engine.menu import MainMenu
from core.battle_state import BattleState

# === Menu ===
menu = MainMenu()
player_team = menu.run()  # returns a list
opponent_team = menu.get_random_team()

# === 1v1 Setup ===
player_pokemon = player_team[0]
enemy_pokemon = opponent_team[0]

# === Battle State ===
battle_state = BattleState(player_pokemon, enemy_pokemon)
battle_state.player_team = [player_pokemon]
battle_state.enemy_team = [enemy_pokemon]
battle_state.selected_team = [player_pokemon]
battle_state.species_pool = menu.species_pool  # fallback if needed

# === Renderer + Battle Loop ===
renderer = GUIRendererDS(battle_state)
battle = BattleLoop(battle_state, renderer)
battle.run()
