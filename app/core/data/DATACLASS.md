TO Use the DataClass from the dataclass module 

from core.data.dataclass import DataClass

data = DataClass(
    
    [
        # Data Sources
        [ {}, {} ],  # Celebrity API
        [ {}, {} ],   # Twitter API
        [ {}, {} ],   #LinkedIn
        ...
    ] 
  )

Note: it has to be a List of list(Data source) of Dictionaries(profiles)

Optionally: Any or all of these "Keyword arguments" can be passed to help filter the results better

            data = DataClass(

                [
                    # Data Sources
                    [ {}, {} ],  # Celebrity API
                    [ {}, {} ],   # Twitter API
                    [ {}, {} ],   #LinkedIn
                    ...
                ],

                name = "john doe", 
                age = 23,
                occupation = "banker",
                gender = 'male',

                )



A very important thing to note is that the DataClass expects the dictionaries to have all of these keys.
So even if there's no value for it, just return the key and value as None.

Secondly, You can pass the occupation as a string or a List(if multiple). The DataClass will handle the complications

Example:

    # Celebrity API

    [
        {
            "name": "elon musk",
            "age": 51,
            "gender": "male",
            "occupation": [

                    "film_producer",
                    "engineer",
            ],
            "vip_score": 8.75,
        },

        {
            "name": "barack obama",
            "age": None,
            "gender": None,
            "occupation": "politics",
            "vip_score": 3,
        },
    ]

Note: all alphabets to be sent should be in lower_case except the None of course as it is a reserved type.


Finally, to execute the Dataclass:

response = data.initiate()


This will return unique profile(s) gotten from all sources.

Please reach out to me (@Huzzy-K) in case of any complications