"""Script test"""

from celebrity_api import CelebrityApi

name = input('Enter Celebrity name:\n')
age = input('Enter Celebrity age:\n')
if age == "":
    age = None
gender = input('Enter Celebrity gender:\n')
if gender == "":
    gender = None
occupation = input('Enter Celebrity occupation:\n')
if occupation == "":
    occupation = None

api = CelebrityApi()

print(api.search(name, age=age, gender=gender, occupation=occupation))
