from engine.game_loop import BattleLoop
from engine.renderer_ds import GUIRendererDS
from engine.menu import MainMenu
from core.battle_state import BattleState

# === Team Selection Menu ===
menu = MainMenu()

player_team = menu.run()              # returns 3 PokémonInstances
opponent_team = menu.get_random_team()  # returns 3 PokémonInstances

# === Create 3v3 Battle State ===
battle_state = BattleState(
    player_team=player_team,
    ai_team=opponent_team
)

# === Renderer + Battle Loop ===
renderer = GUIRendererDS(battle_state)
battle = BattleLoop(battle_state, renderer)
battle.run()
