"""Sourcing from a Celebrity API
API Ninjas - https://api.api-ninjas.com/v1/celebrity
"""

import requests
from .occupation_json import occupation_categories


class CelebrityApi:
    """ Sourcing Class
    This is the main class and it handle the searching and the VIP score calculation.
    """

    def __init__(self):
        self.api_key = 'bBsLtDyj8uxzThYiw1HndQ==RWFIxB620FL6jRbC'

    def process(self, data):
        """ Main function
        It searches the celebrity api.
        
        Args:
            data (dict): Dictionary containing the search parameters
        
        Return:
            List of Dictionaries in the below format:
            {
                'name': str,
                'age': int,
                'gender': str,
                'occupation': List [str],
                'vip_score': int
            }
            or [] is no result was found
        
        """

        name = data.get('name')
        gender = data.get('gender')
        age = data.get('age')
        occupation = data.get('occupation')


        # Input Parameters Check

        if name is None:
            raise ValueError("Name cannot be None") 

        if age is not None:
            try:
                age = int(age)
            except ValueError:
                raise ValueError("Age must be a number")
        else:
            age = age
        
        if gender is not None:
            if gender.lower() not in ['male', 'female']:
                raise ValueError("Gender must either be `male` or `female`")

        if occupation is not None:
            occupation = occupation.lower()

        # API call

        api_url = 'https://api.api-ninjas.com/v1/celebrity?name={}'.format(name)
        """This is the search endpoint of the celebrity api"""

        response = requests.get(api_url, headers={'X-Api-Key': '{}'.format(self.api_key)})

        # filtering

        filtered = []
        return_params = {'name', 'age', 'gender', 'occupation'}

        if response.status_code == requests.codes.ok:
            data = response.json()

            for celeb in data:

                # filling missing attributes
                # this will prevent all the KeyError where ever possible
                for attr in return_params:
                    if attr not in celeb:
                        celeb[attr] = None

                if all(param is None for param in [gender, age, occupation]):
                    # No parameter provided (except for name).
                    filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                    continue
                elif all(param is not None for param in [gender, age, occupation]):
                    # All parameters (Gender, Occupation and Age) provided.
                    if celeb['gender'] == gender.lower() and celeb['age'] == age and occupation in celeb['occupation']:
                        filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                        continue
                elif all(param is not None for param in [gender, age]):
                    # Only Gender and Age provided.
                    if celeb['gender'] == gender.lower() and celeb['age'] == age:
                        filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                        continue
                elif all(param is not None for param in [gender, occupation]):
                    # Only occupation and Gender provided
                    if celeb['gender'] == gender.lower() and occupation in celeb['occupation']:
                        filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                        continue
                elif all(param is not None for param in [occupation, age]):
                    if occupation in celeb['occupation'] and celeb['age'] == age:
                        filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                        continue

                elif occupation is not None:
                    if occupation in celeb['occupation']:
                        filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                        continue

                elif gender is not None:
                    if celeb['gender'] == gender:
                        filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                        continue
                    
                elif age is not None:
                    if celeb['age'] == age:
                        filtered.append({key: celeb[key] for key in celeb.keys() & return_params})
                        continue
                    
            
            # print('{} user(s) found'.format(len(filtered)))

            return self.vip_score(filtered)

        return []
    
    def vip_score(self, filtered_list):
        """Calculates the VIP score
        It using the occupation of the celebrity to calculate the vip score

        Args:
            filtered_list (List): the list of filtered result
        
        Return:
            List of VIPs with their VIP scores.

        """

        for celeb in filtered_list:
            if celeb['occupation'] is not None:
                # occupation present

                celeb_occ_scores = [0]

                for occupation in celeb['occupation']:
                    for category in occupation_categories:
                        if occupation in occupation_categories[category]['occupations']:
                            celeb_occ_scores.append(occupation_categories[category]['popularity_score'])
                celeb['vip_score'] = max(celeb_occ_scores)

        return filtered_list
