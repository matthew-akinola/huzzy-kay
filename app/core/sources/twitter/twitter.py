import os

import tweepy
from decouple import config
# from fastapi import HTTPException


class TwitterAPI:
    """
    Provides a simple, relevance-based search interface to public user accounts on Twitter. 
    Try querying by topical interest, full name, company name, location, or other criteria. 
    Exact match searches are not supported.

    Only the first 1,000 matching results are available.

    Parameters for Authentication

        [CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]

        The simplest way to authenticate is to generate an access token and access token secret 
        through your app’s Keys and Tokens tab under the Twitter Developer Portal Projects & Apps page.

        You’ll also need the app’s API / consumer key and secret that can be found on that page.

        You can then simply pass all four credentials to the OAuth1UserHandler when initializing it.

    """

    def __init__(self) -> None:

        # Private Members of this class

        self.__consumer_key = os.environ.get(
            'CONSUMER_KEY', config('CONSUMER_KEY', default='Ns68HTIORlvaj3jfMAQR9VzoV'))

        self.__consumer_secret = os.environ.get(
            'CONSUMER_SECRET', config('CONSUMER_SECRET', default='vAoVFI7y1oSTAYq8g0WKkggwYttQBkOnC0dsQNb2ti2hUYopmE'))

        self.__access_token = os.environ.get(
            'ACCESS_TOKEN', config('ACCESS_TOKEN', default='1356407126-OhVW66cXVWShjoGoFl6q8BrLtoqXUBH6dkkHMBU'))

        self.__access_token_secret = os.environ.get(
            'ACCESS_TOKEN_SECRET', config('ACCESS_TOKEN_SECRET', default='PrC3wYVmWCq5TvuQxsXvkgytYUjrMmKini85Fj5mbGYUN'))

    def process(self, search_info: dict):
        """
        Parameters for the search_users function:
            q --> The search query to run against people search (required).
         page --> Specifies the page of results to retrieve(optional).
        count --> The number of potential user results to retrieve per page. This value has a maximum of 20 (optional).

        Example response:

            [
                {
                    'name' : 'John Doe',
                    'gender': 'Male',
                    'age': 65,
                    'occupation': [
                        'lawyer',
                        'prosecutor'
                        ],
                    'vip_scrore': 80
                }
            ]

        """

        auth = tweepy.OAuth1UserHandler(
            self.__consumer_key,
            self.__consumer_secret,
            self.__access_token,
            self.__access_token_secret
        )

        api = tweepy.API(auth)

        try:

            user_list = api.search_users(search_info['name'])

        except Exception:
            raise Exception("Unauthorized")

        verified_list = [
            user._json for user in user_list if user._json['verified'] == True]

        profile = dict()
        profile_list = list()

        if verified_list:

            for user in verified_list:
                profile['name'] = user['name']
                profile['age'] = None
                profile['occupation'] = []
                profile['vip_score'] = self.get_vip_score(user)
                profile['gender'] = None

                profile_list.append(profile.copy())

        if profile_list:
            profile_list = [item for item in profile_list if item['vip_score'] > 20]

        return profile_list

    def get_vip_score(self, user):

        if followers := user['followers_count'] > 5 * 10**6:  # super > 5M
            return 100

        elif followers >= 1 * 10**6:  # mega >= 1M
            return 80

        elif followers >= 5 * 10**5:  # pro >= 500k
            return 60

        elif followers >= 1 * 10**5:  # macro >= 100k
            return 40

        else:  # micro 10k and below
            return 20
