

# CELEBRITY API DETAILS
## Name
API Ninja's Celebrities

## Endpoint
https://api.api-ninjas.com/v1/celebrity

## Query Parameter used
- name [str]: Name of the celebrity you wish to search This field is case-insensitive.

## Response Params
- name [str]
- net_worth [int]
- gender [str]
- nationality [str]
- occupation [list]
- height [int]
- birthday [date]
- age [int]
- is_alive [boolean]

## Response Type : JSON (List of Dictionaries)

## Request Limit
50k request per month

# VIP SCORE CALCULATION
## Questions Asked
    - Who is more popular and why?
    - What role does the Relative Age Effect play in celebrities' popularity / vip score?
    - Does their occupation affect how important / popular they are to the public?
    - What message does their networth pass?

## Calculation
For now, I used the occupation of the celebrities in determining their VIP score.

Based on a statistics made by [Statistical](https://www.statista.com/statistics/947376/top-categories-of-celebrities-followed-on-social-media/) with respect to top categories of celebrities, their results shows the following scores for the celebrity categories below:

    Music Artist / Bands - 57%
    Actors/Actresses/TV or movie stars - 50%
    Professional Athletes - 35%
    Reality TV stars - 30%
    Politicians/Political Figures - 25

Using this as a reference point, I recalculated these score on a ration of 100 (with music artist / bands being the hieght). This calculation give me the following score:

    Music Artist / Bands => 99.9% (100 * 57/57)
    Actors/Actresses/TV or movie stars => 87.7% (100 * 50/57)
    Professional Athletes => 61.4% (100 * 35/57)
    Reality TV stars => 52.6% (100 * 30/57)
    Politicians/Political Figures => 43.8 (100 * 25/57)
    Others => 17.5% (100 * 10/57)

## Drawback
The VIP score returns 0 if the celebrity has no occupation returned from the api.

# CODE 
## Parameters
    data = {
        "name": "string" (VIP name to lookup - required)
        "gender": "string" (Gender of celebrity - can be None)
        "age": int (Age of celebrity - can be None)
        "occupation": "string" (Occupation of celebrity - can be None)
    }

## Usage
Import the class

    from ...celebrity_api.celebrity_api import CelebrityAPI

Create an instance of the class

    instance = CelebrityAPI()

Use the `search` method to find VIP (celebrity). Note that the `name` is the only required parameter, others are optional.

    instance.search(name)

## Return
    List of Dictionaries in the below format:
    {
        'name': str,
        'age': int,
        'gender': str,
        'occupation': List [str],
        'vip_score': int
    }
    or [] is no result was found


## Work inprogress
I am looking to create a model that will also include the age and networth of the celebrity (VIP) as I believe these factors affect their popularity and importance.
