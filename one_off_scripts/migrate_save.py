import json
from models import PokemonList, Game

def migrate_save():
    with open("saves/mysave.json", "r+") as f:
        old_save = json.load(f)
    
    with open("saves/living_dex.json", "r+") as f:
        new_save = json.load(f)

    old_save_caught_set = set()
    for item in old_save:
        if item["have"]:
            old_save_caught_set.add(item["name"])

    for item in new_save:
        if item["name"] in old_save_caught_set:
            item["have"] = True
    
    with open("saves/mysave_v2.json", "w+") as f:
        json.dump(new_save, f)

if __name__ == '__main__':
    migrate_save()
    # logic to see missing pokemon, this could be useful somewhere
    # pl = PokemonList()
    # pl.load_from_json()
    # for item in pl.pokemon_list:
    #     if not item.have and Game.sv in item.games:
    #         print(item.name)
