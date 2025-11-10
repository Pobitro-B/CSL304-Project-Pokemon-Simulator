import os
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://bulbapedia.bulbagarden.net"
OUTPUT_DIR = "sprites_b2w2_first151"
HEADERS = {"User-Agent": "Mozilla/5.0"}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_html(url):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.text

def download_image(url, path):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)

def extract_b2w2_sprites(html):
    soup = BeautifulSoup(html, "html.parser")
    # Find the <tr> that contains the Black/White and Black2/White2 table header
    tables = soup.find_all("table", string=re.compile("Black and White Versions 2"))
    if not tables:
        tables = soup.find_all("table", text=re.compile("Black 2"))

    # fallback if search by text fails
    if not tables:
        tables = soup.find_all("table", style=re.compile("background:#FFF"))
    
    images = []
    for table in tables:
        if not table.find("a", href=re.compile("Black_and_White_Versions_2")):
            continue
        imgs = table.find_all("img")
        for img in imgs:
            src = img.get("src")
            if src.startswith("//"):
                src = "https:" + src
            images.append(src)
    # There should be 4 images (front/back for both Black 2 and White 2)
    return list(dict.fromkeys(images))  # remove dupes while preserving order

def main():
    pokedex = [
        "Bulbasaur","Ivysaur","Venusaur","Charmander","Charmeleon","Charizard",
        "Squirtle","Wartortle","Blastoise","Caterpie","Metapod","Butterfree",
        "Weedle","Kakuna","Beedrill","Pidgey","Pidgeotto","Pidgeot","Rattata","Raticate",
        "Spearow","Fearow","Ekans","Arbok","Pikachu","Raichu","Sandshrew","Sandslash",
        "Nidoran♀","Nidorina","Nidoqueen","Nidoran♂","Nidorino","Nidoking","Clefairy",
        "Clefable","Vulpix","Ninetales","Jigglypuff","Wigglytuff","Zubat","Golbat","Oddish",
        "Gloom","Vileplume","Paras","Parasect","Venonat","Venomoth","Diglett","Dugtrio",
        "Meowth","Persian","Psyduck","Golduck","Mankey","Primeape","Growlithe","Arcanine",
        "Poliwag","Poliwhirl","Poliwrath","Abra","Kadabra","Alakazam","Machop","Machoke",
        "Machamp","Bellsprout","Weepinbell","Victreebel","Tentacool","Tentacruel","Geodude",
        "Graveler","Golem","Ponyta","Rapidash","Slowpoke","Slowbro","Magnemite","Magneton",
        "Farfetch’d","Doduo","Dodrio","Seel","Dewgong","Grimer","Muk","Shellder","Cloyster",
        "Gastly","Haunter","Gengar","Onix","Drowzee","Hypno","Krabby","Kingler","Voltorb",
        "Electrode","Exeggcute","Exeggutor","Cubone","Marowak","Hitmonlee","Hitmonchan",
        "Lickitung","Koffing","Weezing","Rhyhorn","Rhydon","Chansey","Tangela","Kangaskhan",
        "Horsea","Seadra","Goldeen","Seaking","Staryu","Starmie","Mr._Mime","Scyther",
        "Jynx","Electabuzz","Magmar","Pinsir","Tauros","Magikarp","Gyarados","Lapras",
        "Ditto","Eevee","Vaporeon","Jolteon","Flareon","Porygon","Omanyte","Omastar",
        "Kabuto","Kabutops","Aerodactyl","Snorlax","Articuno","Zapdos","Moltres","Dratini",
        "Dragonair","Dragonite","Mewtwo","Mew"
    ]

    for idx, name in enumerate(pokedex, 1):
        print(f"\n[{idx:03d}] {name}")
        page_url = f"{BASE_URL}/wiki/{name.replace(' ', '_')}_(Pokémon)"
        try:
            html = fetch_html(page_url)
            sprite_urls = extract_b2w2_sprites(html)
            if not sprite_urls:
                print("  No B2W2 sprites found.")
                continue
            for i, img_url in enumerate(sprite_urls, 1):
                ext = os.path.splitext(img_url)[-1]
                filename = f"{idx:03d}_{name}_b2w2_{i}{ext}"
                save_path = os.path.join(OUTPUT_DIR, filename)
                print(f"  Downloading: {img_url}")
                download_image(img_url, save_path)
            time.sleep(1)
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()
