import wikipedia
import requests
import openai
import datetime
import sys
from core.settings import settings
from SPARQLWrapper import SPARQLWrapper, JSON


openai.api_key = settings.OPEN_API_KEY
endpoint_url = "https://query.wikidata.org/sparql"


def calculate_age_in_years(born, died=None):
    if died:
        return died.year - born.year - ((died.month, died.day) < (born.month, born.day))
    else:
        return (
            datetime.date.today().year
            - born.year
            - (
                (datetime.date.today().month, datetime.date.today().day)
                < (born.month, born.day)
            )
        )


def get_wiki_data(entityID):
    """
    Executes SPARQL query to get data from wikidata
    """

    args = {"entityID": entityID}

    query = """SELECT  ?genderLabel ?occupationLabel ?dateOfBirth ?dateOfDeath  {{
        VALUES (?item) {{ (wd:{entityID}) }}
        OPTIONAL {{ ?item wdt:P21 ?gender . }}
        OPTIONAL {{ ?item wdt:P106 ?occupation . }}
        OPTIONAL {{ ?item wdt:P569 ?dateOfBirth . }}
        OPTIONAL {{ ?item wdt:P570 ?dateOfDeath . }}

        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}""".format(
        **args
    )

    user_agent = "WDQS-example Python/%s.%s" % (
        sys.version_info[0],
        sys.version_info[1],
    )
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    raw_results = sparql.query().convert()
    results = raw_results["results"]["bindings"]
    return results


class Wiki_Source:
    """
    This class is used for getting the data from Wikipedia & Wikidata with vip_score calculated by gpt3 \n
    Param - full_name -> str
    """

    def get_vip_score(self, full_name):
        """
        This function gets a description of the person from Wikipedia and uses GPT-3 to calculate the VIP score of the person.
        """
        try:
            # Get the data from wikipedia
            wikipedia_resp = wikipedia.page(
                title=f"{full_name}", auto_suggest=True
            ).content
            # Get the first paragraph of the wikipedia page
            wikipedia_desc = (
                wikipedia_resp.split("\n")[0] + "\n" + wikipedia_resp.split("\n")[1]
            )

            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"I am a highly intelligent bot trained to simulate human perception. I can read a description of a person and return a number between 0 and 100 indicating how important humans would think the person is. \n\nDescription: {wikipedia_desc} .\n\nHow important is this person? Answer with only a number.",
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

            vip_score = response["choices"][0]["text"]
            # Strip the vip score of the newline character
            vip_score = vip_score.strip()
            # Convert the vip score to an integer
            vip_score = int(vip_score)

            return vip_score
        except:
            return None

    def get_canonical_data(self, full_name):
        """
        This function gets the gender and occupation of the person from Wikidata.
        """
        try:
            # Get wikidata entity id
            entity_id = requests.get(
                f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={full_name}&language=en&format=json"
            ).json()["search"][0]["id"]

            # Get the data from wikidata
            wikidata_resp = get_wiki_data(entity_id)

            if len(wikidata_resp) == 0:
                return {}

            wikidata_resp = wikidata_resp[0]

            gender = wikidata_resp["genderLabel"]["value"]
            occupation = wikidata_resp["occupationLabel"]["value"]
            date_of_birth = wikidata_resp["dateOfBirth"]["value"]
            date_of_birth = datetime.datetime.strptime(
                date_of_birth, "%Y-%m-%dT%H:%M:%SZ"
            )
            date_of_death = (
                wikidata_resp["dateOfDeath"]["value"]
                if "dateOfDeath" in wikidata_resp
                else None
            )
            date_of_death = (
                datetime.datetime.strptime(date_of_death, "%Y-%m-%dT%H:%M:%SZ")
                if date_of_death
                else None
            )
            age = calculate_age_in_years(date_of_birth, date_of_death)

            return {
                "gender": gender,
                "occupation": occupation,
                "age": age,
            }

        except Exception as e:
            return None

    def process(self, dict_):
        full_name = dict_["name"]

        vip_score = self.get_vip_score(full_name)
        # If vip score is none, nobody was found
        if vip_score is None:
            return []

        canonical_data = self.get_canonical_data(full_name)

        is_vip = vip_score > 50

        if canonical_data is None:
            return []

        return [
            {
                "name": full_name,
                "gender": canonical_data["gender"],
                "occupation": canonical_data["occupation"],
                "age": canonical_data["age"],
                "is_vip": is_vip,
                "vip_score": vip_score,
            }
        ]
