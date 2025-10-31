from engine.game_loop import BattleLoop
from engine.renderer import GUIRenderer
from core.pokemon import PokemonSpecies
from core.move import Move
from core.pokemon import PokemonInstance
from core.battle_state import BattleState
from engine.action import Action

# Moves
flamethrower = Move("Flamethrower", "Fire", 90, 100, "special")
water_gun = Move("Water Gun", "Water", 40, 100, "special")
tackle = Move("Tackle", "Normal", 40, 100, "physical")
rock_slide = Move("Rock Slide", "Rock", 75, 90, "physical")

# Pokémon species definitions
species_charizard = PokemonSpecies(
    name="Charizard",
    types=["Fire","Flying"],
    base_stats={"hp": 78, "atk": 84, "def": 78, "speed": 100, "spatk": 109, "spdef": 85},
    default_ability="Blaze",
    height_m=1.7,
    weight_kg=90.5,
    pokedex_entry="It spits fire that is hot enough to melt boulders.",
    front_sprite="Poké_Ball_icon.svg.png",  # placeholder image
    back_sprite="Poké_Ball_icon.svg.png"
)

species_blastoise = PokemonSpecies(
    name="Blastoise",
    types=["Water"],
    base_stats={"hp": 79, "atk": 83, "def": 100, "speed": 78, "spatk": 85, "spdef": 105},
    default_ability="Torrent",
    height_m=1.6,
    weight_kg=85.5,
    pokedex_entry="A brutal Pokémon with pressurized water jets on its shell.",
    front_sprite="Poké_Ball_icon.svg.png",
    back_sprite="Poké_Ball_icon.svg.png"
)

# Pokémon instances
charizard = PokemonInstance(species_charizard, level=50, moves=[flamethrower, rock_slide])
blastoise = PokemonInstance(species_blastoise, level=50, moves=[water_gun, tackle])

# Example setup (assuming you already defined Pokémon and moves)
battle_state = BattleState(charizard, blastoise)
renderer = GUIRenderer(battle_state)

battle = BattleLoop(battle_state, renderer)
battle.run()

