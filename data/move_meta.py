import requests
import json

# --- Load MOVE_POOL from movesets.py ---
from movesets import MOVE_POOL

# --- Pull moves from Pokémon Showdown ---
moves_db = requests.get("https://play.pokemonshowdown.com/data/moves.json").json()

def normalize_accuracy(acc):
    if acc is True:
        return 100
    if acc is False:
        return 0
    return acc or 100

# --- Build metadata only for moves we actually need ---
all_moves = {move for moves in MOVE_POOL.values() for move in moves}

MOVE_METADATA = {}

# Reverse lookup because Showdown keys aren't title-cased
name_map = {data["name"]: data for data in moves_db.values()}

for move in all_moves:
    if move not in name_map:
        print(f"[WARN] Move '{move}' not found in Showdown DB. Skipping.")
        continue

    data = name_map[move]

    MOVE_METADATA[move] = {
        "MoveType": data.get("type", "Normal"),
        "Power": data.get("basePower", 0),
        "Accuracy": normalize_accuracy(data.get("accuracy", 100)),
        "Category": data.get("category", "Status").lower()
    }

# Save metadata
with open("move_metadata.py", "w") as f:
    f.write("MOVE_METADATA = ")
    f.write(json.dumps(MOVE_METADATA, indent=4))

print("Done → move_metadata.py created successfully!")
