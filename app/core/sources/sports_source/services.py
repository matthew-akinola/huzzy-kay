from datetime import date
import json
import os

real_path = os.path.dirname(os.path.realpath(__file__))
jdata = json.loads(open (real_path + '/players.json').read())

today = date.today()

class SearchService:
    # def _init_(self, info:dict):
    #     self.info = info

    def process(self, search_info:dict):
        if  search_info:
            name = search_info['name']
            name = name.split(' ')
            new_name = [item.capitalize() for item in name]
            name = ''.join(new_name)
            new_players = []
            for player in jdata['data']:
                if player['display_name'].find(name) != -1:
                    age = player['date_of_birth'][:4]
                    new_age = int(today.year) - int(age)
                    new_players.append(self.data_hold(
                        player['display_name'], 
                        new_age, 
                        player['gender'], 
                        self.occupation(player['position_id']), 
                        self.vip_score(new_age, player['position_id']), 
                        True)
                    ) 
            return new_players
        else:
            return []

    def occupation(self, position):
        if position is not None:
            return 'player'      
        return 'footballer'  

    def data_hold(
        self,
        name = None, 
        age = None, gen = None,  
        occ = None, score = 0, boo = False
        ):
        return {
            "name": name,
            "age": age,
            "gender": gen,
            "occupation": occ,
            "vip_score": score,
            "is_vip": boo
        }
    
    def vip_score(self, age:int, position):
        _score = 0
        if age <= 25 and position is not None:
            _score = 80
        elif age > 25 and age <= 39 and position is not None:
            _score = 40
        elif age > 39 and age <= 64 and position is not None:
            _score = 20
        elif age > 64 and position is not None:
            _score = 60
        else:
            _score = 10
        return _score

