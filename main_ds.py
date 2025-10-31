from engine.game_loop import BattleLoop
from engine.renderer_ds import GUIRendererDS  # new DS-style renderer
from core.pokemon import PokemonSpecies, PokemonInstance
from core.move import Move
from core.battle_state import BattleState

# === Moves ===
flamethrower = Move("Flamethrower", "Fire", 90, 100, "special")
water_gun = Move("Water Gun", "Water", 40, 100, "special")
tackle = Move("Tackle", "Normal", 40, 100, "physical")
rock_slide = Move("Rock Slide", "Rock", 75, 90, "physical")

# === Pokémon species definitions ===
species_charizard = PokemonSpecies(
    name="Charizard",
    types=["Fire", "Flying"],
    base_stats={"hp": 78, "atk": 84, "def": 78, "speed": 100, "spatk": 109, "spdef": 85},
    default_ability="Blaze",
    height_m=1.7,
    weight_kg=90.5,
    pokedex_entry="It spits fire that is hot enough to melt boulders.",
    front_sprite="assets/charizard_front.png",  # replace with actual sprites later
    back_sprite="assets/charizard_back.png"
)

species_blastoise = PokemonSpecies(
    name="Blastoise",
    types=["Water"],
    base_stats={"hp": 79, "atk": 83, "def": 100, "speed": 78, "spatk": 85, "spdef": 105},
    default_ability="Torrent",
    height_m=1.6,
    weight_kg=85.5,
    pokedex_entry="A brutal Pokémon with pressurized water jets on its shell.",
    front_sprite="assets/blastoise_front.png",
    back_sprite="assets/blastoise_back.png"
)

# === Pokémon instances ===
charizard = PokemonInstance(species_charizard, level=50, moves=[flamethrower, rock_slide])
blastoise = PokemonInstance(species_blastoise, level=50, moves=[water_gun, tackle])

# === Battle setup ===
battle_state = BattleState(charizard, blastoise)
renderer = GUIRendererDS(battle_state)

battle = BattleLoop(battle_state, renderer)
battle.run()
