from __future__ import annotations
import csv

import tkinter as tk
import sys
import urllib.request
import zipfile
from pathlib import Path
from dotenv import load_dotenv

from models import PokemonList, GUI

load_dotenv()

def extract_sprites():
    """Extract all sprites on initial run"""
    project_root = Path(__file__).resolve().parent.parent

    zip_path = project_root / "resources" / "pokemon_sprites.zip"
    extract_to_dir = project_root / "resources" / "pokemon_sprites"
    
    if not zip_path.exists():
        print("downloading sprites from github..")
        url = "https://github.com/masonkimbell/pokemon-living-dex-tracker/releases/download/v1.0.0/pokemon_sprites.zip"
        urllib.request.urlretrieve(url, zip_path)
        print("download complete")

    if not extract_to_dir.exists():
        print(f"extracting pokemon sprites..")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # extracts everything cleanly into the 'resources/pokemon_sprites' folder
                zip_ref.extractall(extract_to_dir)
            print("successfuly extracted sprites")
        except Exception as e:
            print(f"failed to extract sprites: {e}")
            sys.exit(1)

def main():
    all_pokemon = PokemonList()
    try:
        with open("saves/shinylivingdex.json") as f:
            print("opening with saved json data")
            all_pokemon.load_from_json()
    except FileNotFoundError:
        with open("resources/shinylivingdex.csv") as f:
            print("opening with csv")
            reader_obj = csv.reader(f)

            for row in reader_obj:
                if "Shinydex" in row:
                    continue
                all_pokemon.add_pokemon(row)
            all_pokemon.sort_by_region()
            all_pokemon.save_to_json()

    all_pokemon.init_boxes()

    root = tk.Tk()
    root.title("Pokemon Living Dex Organizer")
    root.geometry("1400x900")  # Optional: Set window size
    app = GUI(root, all_pokemon)
    root.mainloop()


if __name__ == "__main__":
    extract_sprites()
    main()
