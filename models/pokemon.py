from __future__ import annotations
import json
import os
from .pokedex import EntryRow
from .region import Region


class Pokemon:
    def __init__(self, entry: EntryRow, row: list = [], prev: Pokemon = None):
        if entry:
            self.name: str = entry['name']
            self.number: str = entry['number']
            self.region: Region = Region(entry['region'])
            self.form: int = entry['form']
            self.have: bool = entry['have']
            self.image_path: str = entry['image_path']
        if row:
            self.entry = {}

            name: str = row[5]
            replaced = False
            if "â™‚" in name:
                name = name.split(" â™‚")[0].split("â™‚")[0]
                name = f"{name} Male"
                replaced = True
            if "â™€" in name:
                name = name.split(" â™€")[0].split("â™€")[0]
                name = f"{name} Female"
                replaced = True
            if "Ã©" in name:
                name = name.replace("Ã©", "e")
            number = row[6]
            if number == "":
                number = prev.number

            self.form = 0
            self.number = number

            if prev and not replaced:
                if self.number == prev.number:
                    self.form = prev.form + 1

            if "_a" in row[4] and "Alolan" in row[5]:
                self.region = Region.ALOLA_VARIANTS
            elif "_g" in row[4] and "Galarian" in row[5]:
                self.region = Region.GALAR_VARIANTS
            elif "_h" in row[4] and "Hisuian" in row[5]:
                self.region = Region.HISUI_VARIANTS
            elif "_p" in row[4] and "Paldean" in row[5]:
                self.region = Region.PALDEA_VARIANTS
            elif int(self.number) > 0 and int(self.number) <= 151:
                self.region = Region.KANTO
            elif int(self.number) >= 152 and int(self.number) <= 251:
                self.region = Region.JOHTO
            elif int(self.number) >= 252 and int(self.number) <= 386:
                self.region = Region.HOENN
            elif int(self.number) >= 387 and int(self.number) <= 493:
                self.region = Region.SINNOH
            elif int(self.number) >= 494 and int(self.number) <= 649:
                self.region = Region.UNOVA
            elif int(self.number) >= 650 and int(self.number) <= 721:
                self.region = Region.KALOS
            elif int(self.number) >= 722 and int(self.number) <= 807:
                self.region = Region.ALOLA
            elif int(self.number) >= 808 and int(self.number) <= 809:
                self.region = Region.UNKNOWN
            elif int(self.number) >= 810 and int(self.number) <= 898:
                self.region = Region.GALAR
            elif int(self.number) >= 899 and int(self.number) <= 905:
                self.region = Region.HISUI
            elif int(self.number) >= 906 and int(self.number) <= 1010:
                self.region = Region.PALDEA
            elif int(self.number) >= 1011 and int(self.number) <= 1017:
                self.region = Region.KITAKAMI
            elif int(self.number) >= 1018 and int(self.number) <= 1025:
                self.region = Region.BLUEBERRY

            self.name = name
            self.have = False
            self.image_path = self.get_image_path()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_image_path(self):
        gender = []
        if " Female" in self.name and self.number != 29:  # Nidoran F
            if int(self.number) == 255:  # Torchic doesn't have different front sprites
                gender = ["md"]
            else:
                gender = ["fd"]
        if " Male" in self.name and int(self.number) != 32:  # Nidoran M
            gender = ["md"]

        if (
            int(self.number) in [215] and "Hisui" in self.name
        ):  # Hisuian Sneasel has forms and gender differences
            self.form += 1

        if int(self.number) == 774:  # Minior only has one shiny form
            self.form = 7

        if int(self.number) == 80 and self.form == 1:  # Slowbro form 1 is the mega
            self.form = 2

        if int(self.number) in [
            854,
            855,
            1012,
            1013,
        ]:  # Sinistea, Polteageist, Poltchageist, Sinistcha
            self.form = 0

        if int(self.number) == 876 and 'Female' in self.name:
            self.form = 1 # Indeedee

        if self.form < 10:
            form_id_str = f"00{self.form}"
        elif self.form < 100:
            form_id_str = f"0{self.form}"
        else:
            form_id_str = self.form

        possible_genders = ["mf", "uk", "mo", "fo"] + gender
        for g in possible_genders:
            if int(self.number) == 869:  # Alcremie
                fname = (
                    f"poke_capture_{self.number}_000_{g}_n_00000{form_id_str}_f_n.png"
                )
            else:
                fname = (
                    f"poke_capture_{self.number}_{form_id_str}_{g}_n_00000000_f_n.png"
                )
            path = os.path.join("resources", "pokemon_sprites", fname)
            try:
                with open(path) as f:
                    # print(path)
                    return path
            except FileNotFoundError:
                continue

        # print(path)

    def to_dict(self):
        return {
            'name': self.name,
            'number': int(self.number),
            'number_str': self.number,
            'region': self.region.value,
            'form': self.form,
            'have': self.have,
            'image_path': self.image_path
        }


class PokemonList:
    pokemon_list: list[Pokemon] = []
    boxes = []

    def find(self, number, form_id):
        for item in self.pokemon_list:
            if item.number == number and item.form == form_id:
                return item

        return None

    def add_pokemon(self, row):
        try:
            prev_pokemon = self.pokemon_list[-1]
        except IndexError:
            prev_pokemon = None
        p = Pokemon(None, row, prev_pokemon)
        self.pokemon_list.append(p)

    def print(self):
        for item in self.pokemon_list:
            print(item.entry)

    def load_from_json(self):
        self.pokemon_list = []
        with open("saves/shinylivingdex.json", "r+") as f:
            data = json.load(f)
        for item in data:
            self.pokemon_list.append(Pokemon(item))

    def save_to_json(self):
        out_json = []
        for item in self.pokemon_list:
            out_json.append(item.to_dict())

        with open("saves/shinylivingdex.json", "w+") as f:
            json.dump(out_json, f)


    def sort_by_region(self):
        """Sort PokemonList first by region, then by national dex number"""
        buckets: list[list[Pokemon]] = [[] for i in range(len(Region))]

        # add to correct bucket
        for item in self.pokemon_list:
            bucket_no = item.region.value - 1
            buckets[bucket_no].append(item)

        # flatten
        final_list: list[Pokemon] = []
        for bucket in buckets:
            for item in bucket:
                final_list.append(item)

        self.pokemon_list = final_list

    
    def filter_by_region(self, region_filter: list[Region]) -> PokemonList:
        """Return only Pokemon in the selected regions"""
        sublist = PokemonList()
        for item in self.pokemon_list:
            if item.region in region_filter:
                sublist.pokemon_list.append(item)

        sublist.init_boxes()
        return sublist


    def init_boxes(self):
        """Format Pokemon list into pages of 6x5 grids"""
        grid = []
        subgrid = []
        for item in self.pokemon_list:
            subgrid.append(item)
            if len(subgrid) == 30:
                grid.append(subgrid)
                subgrid = []
        if len(subgrid) > 0:
            grid.append(subgrid)

        boxes = []

        subgrid = []
        for i, items in enumerate(grid):
            box = []
            for item in items:
                subgrid.append(item)
                if len(subgrid) == 6:
                    box.append(subgrid)
                    subgrid = []
            if len(subgrid) > 0:
                box.append(subgrid)
            boxes.append(box)
        self.boxes = boxes


    def clear(self):
        """Empty the PokemonList and Boxes"""
        self.pokemon_list.clear()
        self.boxes.clear()
