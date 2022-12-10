import json
import re
import pandas as pd
import os

class ForbesVip():

    def make_result(self, data: str) -> dict:
        local_dict = {}
        data_con = data.split(";")
        for i in data_con:
            j = i.split(":")
            local_dict[j[0]] = j[1]
        return self.dict_to_json(local_dict)

    def dict_to_json(self, data: dict):
        json_data = json.dumps(data)
        # return dict(json.loads(json_data))
        return data

        pass

    def process(self, pname: dict):
        """
        takes a name and search for it through the forbes
        database
        @param pname: the name to be search
        @return: a list of dictionary
        """
        result_list = []

        # df = frb_list.get_df('billionaires')
        real_path = os.path.dirname(os.path.realpath(__file__))
        df = pd.read_csv(real_path + "/forbes_list.csv")

        len = df.firstName.size

        for i in range(len):
            name = str(df.firstName[i]) + " " + str(df.lastName[i])
            industry = str(df.category[i])
            country = str(df.country[i])
            age = int(df.age[i]) if df.age[i] >= 0 else 0
            gender = "Male" if df.gender[i] == "M" else "Female"
            vip_score = 30
            worth = int(df.finalWorth[i]) if df.finalWorth[i] >= 0 else 0

            if worth >= 200000:
                vip_score += 70
            elif worth >= 150000:
                vip_score += 60
            elif worth >= 100000:
                vip_score += 50
            elif worth >= 75000:
                vip_score += 40
            elif worth >= 50000:
                vip_score += 30
            elif worth >= 25000:
                vip_score += 20
            elif worth >= 10000:
                vip_score += 10
            elif worth >= 5000:
                vip_score += 5
            elif worth >= 1000:
                vip_score += 2
            else:
                vip_score = vip_score

            diction = {
                "name": name,
                "occupation": [industry],
                # "country": country,
                "age": age,
                "gender": gender,
                "vip_score": vip_score,
            }
            # compile name passed to regex pattern
            namep = re.compile(pname['name'].lower())

            # search if name pattern is in the name variable
            if namep.search(name.lower()):
                result_list.append(diction)
                # result_list.append(self.make_result(data))
        return result_list


vip = ForbesVip()
