import pygame
import threading
import time

from engine.game_loop import BattleLoop
from engine.renderer_ds import GUIRendererDS
from engine.menu import MainMenu
from core.battle_state import BattleState

# ================================================================
# 🎵 NON-BLOCKING BACKGROUND MUSIC STARTUP
# ================================================================

def start_music():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("battle_theme.mp3")
        pygame.mixer.music.play(-1)  # Loop forever
    except Exception as e:
        print(f"[Audio Warning] Could not play music: {e}")

# Run music startup in a thread so it doesn't freeze Tkinter
threading.Thread(target=start_music, daemon=True).start()

# ================================================================
# 🧭 TEAM SELECTION
# ================================================================

menu = MainMenu()

player_team = menu.run()              # returns list of PokémonInstances
opponent_team = menu.get_random_team()  # returns list of PokémonInstances

# ================================================================
# ⚔ CREATE 3v3 BATTLE STATE
# ================================================================

battle_state = BattleState(
    player_team=player_team,
    ai_team=opponent_team
)

# ================================================================
# 🎨 RENDERER + GAME LOOP
# ================================================================

renderer = GUIRendererDS(battle_state)
battle = BattleLoop(battle_state, renderer)
battle.run()

# ================================================================
# 🛑 OPTIONAL: clean stop on exit
# ================================================================
try:
    pygame.mixer.music.stop()
except:
    pass
