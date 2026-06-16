from .base import APIClient
from data.constants import GAMES_TO_POKEAPI_POKEDEX

class PokeAPI(APIClient):
    def __init__(self):
        super().__init__('https://pokeapi.co/api/v2')

    def get_all_pokedex(self) -> tuple[dict, int]:
        response, status_code = self.get('pokedex', {'limit': 50})
        return response, status_code

    def get_pokedex_by_game(self, game: str) -> tuple[dict, int]:
        game_list = GAMES_TO_POKEAPI_POKEDEX[game]
        full_game_results: list[int] = []

        all_games, status_code = self.get_all_pokedex()
        if status_code != 200:
            print('error getting list of all games')
            return
                
        for game in all_games['results']:
            if game['name'] in game_list:
                pokeapi_game_pk = game['url'].split('/')[-2]
                game_results, status_code = self.get(f'pokedex/{pokeapi_game_pk}')
                if status_code != 200:
                    print(f'error getting list for {game["name"]} pokedex')
                    return
                pokemon_entries = game_results['pokemon_entries']
                just_numbers = [int(e['pokemon_species']['url'].split('/')[-2]) for e in pokemon_entries]
                full_game_results += just_numbers

        no_dupes = list(dict.fromkeys(full_game_results))

        return no_dupes, status_code
