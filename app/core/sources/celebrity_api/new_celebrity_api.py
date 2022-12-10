import os

import requests
from decouple import config

from .occupation_json import occupation_categories

headers = {
    "X-Api-Key": os.environ.get("NINJA_API_KEY",
                                config("NINJA_API_KEY", default="PrPZBhuzPYXJ9JKclhnAgw==xNG59PA9Buscg009"))
}

base_url = "https://api.api-ninjas.com/v1/celebrity?name="


class CelebrityAPI:
    """
    This Celebrity API gets response by sending a name to API Ninja Celebrity API endpoint

    """

    def process(self, search_query):

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
        response = requests.get(
            url=base_url+search_query['name'], headers=headers)

        result = response.json()

        profile = dict()

        profile_list = list()

        if result:
            for item in result:

                profile['name'] = item['name']
                profile['age'] = item.get('age', None)
                profile['gender'] = item.get('gender', None)
                profile['occupation'] = item.get('occupation', [])
                profile['vip_score'] = 10  # initial vip score

                profile_list.append(profile.copy())

            return self.vip_score(profile_list)

        return profile_list # Empty list

    def vip_score(self, profile_list):
        """Calculates the VIP score
        It using the occupation of the celebrity to calculate the vip score

        Args:
            filtered_list (List): the list of filtered result

        Return:
            List of VIPs with their VIP scores.

        """

        for profile in profile_list:
            if profile['occupation']:
                # occupation present

                occupation_scores = [0]

                for occupation in profile['occupation']:
                    for category in occupation_categories:
                        if occupation in occupation_categories[category]['occupations']:
                            occupation_scores.append(
                                occupation_categories[category]['popularity_score'])

                profile['vip_score'] = max(occupation_scores)

        return profile_list
