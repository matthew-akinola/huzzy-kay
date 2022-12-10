import json
import math
from fastapi import HTTPException, status


class DataClass:
    """
    A dataclass that taskes an array of lists of dictionaries,
    sort out the data, calculate an average vip score and
    return unique profile(s)

    Args:
         data_list: List
         **kwargs: name, age, occupation etc.

    Returns:
        List()
    """

    def __init__(self, data_list, **kwargs):
        self.kwargs = kwargs
        self.data_list = data_list

        # making sure the argument passed is a list
        if not isinstance(data_list, list):
            return "Error: data list must be a list type"

    def initiate(self):
        """A function that must be called to instantiate the class"""

        unique_list = self.extract_unique()

        cleaned_data = self.clean(unique_list)

        return cleaned_data

    def extract_unique(self):
        """A function that filters the data list and return the unique result(s)"""

        converts = []

        final = []

        new_results = self.filter_check()

        for obj in new_results:
            converted_dicts = {json.dumps(par) for par in obj}

            converts.append(converted_dicts)

        for item in converts:
            # Using Set Union Operation to remove duplicate entry
            converts[0] |= item

            final = converts[0]

        final = [json.loads(item) for item in final]

        return final

    def get_average_vip_score(self, package):

        scores = [item.get("vip_score", 0) for item in package]

        try:
            average = sum(scores) / len(package)
        except:
            return None

        return average

    def clean(self, unique_list):

        profile_list = []

        for item in unique_list:
            pre_list = [
                piece
                for piece in unique_list
                if piece["name"].lower() == item["name"].lower()
            ]

            item["vip_score"] = self.get_average_vip_score(pre_list)

            item["is_vip"] = True

            item["occupation"] = self.merge_occupations(pre_list)

            item["gender"] = self.process_gender(pre_list)

            # in case of diffent age from different data source
            item["age"] = self.process_duplicate_age(pre_list)

            profile_list.append(item)

            # Remove all profiles with same name after processing it
            for trojan in unique_list:
                if trojan["name"].lower() == item["name"].lower():
                    unique_list.remove(trojan)

        # Convert all values to lowercase

        clean_list = []
        for profile in profile_list:

            data = {
                key: value.lower() if isinstance(value, str) else value
                for key, value in profile.items()
            }

            clean_list.append(data)

        return clean_list

    def process_gender(self, pre_list):

        # filter out null values

        multiple_gender = [
            item["gender"].lower() for item in pre_list if item["gender"]
        ]

        if multiple_gender:

            # Pick Gender with the highest occurence

            return max(multiple_gender, key=multiple_gender.count)

        return None

    def merge_occupations(self, pre_list):
        """
        A function that merges the occupation for unique
        users from many list(source)
        """
        occupation = []
        for item in pre_list:

            value = item.get("occupation")

            if isinstance(value, str):
                value = [value]

            try:
                occupation.extend(value)
            except:
                pass

        return list(set(occupation))

    def process_duplicate_age(self, pre_list):
        """
        A function that calculates the average possible age
        if the age for a user differs per source(list)
        """

        ages = []
        for item in pre_list:
            if item["age"] != None:
                age = int(item["age"])
                ages.append(age)

        try:
            age = math.ceil(sum(ages) / len(ages))

        except ZeroDivisionError:

            return None

        return age

    def filter_check(self):

        parameters = list(self.kwargs.values())

        # convert all strings to lowerccase, ensure no null values

        parameters = [
            item.lower() if isinstance(item, str) else item
            for item in parameters
            if item
        ]

        try:
            # convert numeric filter like age to int
            parameters = [
                int(item) if item.isnumeric() else item for item in parameters if item
            ]
        except:
            # if raw JSON request was sent, then pass
            pass

        kwargs = self.kwargs

        new_results = []

        data_list = list(filter(None, self.data_list))

        for data in data_list:

            # initial
            filtered_list = data

            # name_filter
            if kwargs.get("name", ""):
                filtered_list = [
                    item
                    for item in filtered_list
                    if kwargs.get("name", "").lower() in item.get("name").lower()
                ]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="name is required"
                )

            # gender_filter
            if kwargs.get("gender", ""):
                filtered_list = [
                    item
                    for item in filtered_list
                    if item["gender"] is not None
                    if item["gender"].lower() in parameters
                ]

            # age_filter
            if kwargs.get("age", ""):
                filtered_list = [
                    item for item in filtered_list if item["age"] in parameters
                ]

            # occupation_filter
            if kwargs.get("occupation", ""):

                for item in filtered_list:
                    occupation = item["occupation"]

                    if isinstance(occupation, str):  # A single occupation in lowercase
                        occupation = occupation.lower()

                    if isinstance(
                        occupation, list
                    ):  # A list of occupations in lowercase
                        occupation = [work_field.lower() for work_field in occupation]

                filtered_list = [
                    item
                    for item in filtered_list
                    if kwargs["occupation"].lower() in occupation
                ]

            if filtered_list:
                new_results.append(filtered_list)

        return new_results
