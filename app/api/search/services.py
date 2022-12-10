from fastapi import Depends
from db.db import db_session
from db.models.history import History
from db.models.people import People
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.processing.process import Process
from .schemas import SearchParamsSchema, SearchResponseSchema
from ..user.schemas import PeopleCreateSchema
from ..history.services import HistoryService

class SearchService:
    def __init__(self, session: AsyncSession = Depends(db_session)):
        self.session = session

    async def vip_sorting(self, vip_lists: list):
        for vip_list in vip_lists:
            for vip in vip_list:  
                if  vip['vip_score'] >= 90:
                    vip['category'] = 'gold'
                elif vip["vip_score"] >= 55 and vip["vip_score"] < 90:
                    vip["category"] = "silver"
                else:
                    vip["category"] = "bronze"
        return vip_list


    async def search(self, query: SearchParamsSchema, user_id : None) -> SearchResponseSchema:
        # Check if the person exists in the database on single search case
        if type(query) != list:
            person = await self.session.execute(
                select(People)
                .where(People.name == str(query["name"]).lower())
                .where(People.age == query["age"])
                .where(People.gender == query["gender"])
                .where(People.occupation == query["occupation"])
            )

            person = person.scalars().first()

            # If the person exists, return the person
            if person:
                person = person.__dict__
                # Construct record to save to history
                response = {
                    "name": person["name"],
                    "age": person["age"],
                    "gender": person["gender"],
                    "occupation": person["occupation"],
                    "vip_score": person["vip_score"],
                    "is_vip": person["is_vip"],
                }

                query["result_id"] = person["id"]

                # Save query to history
                history = await HistoryService(self.session).create_history(query, response, user_id)


                # Construct response
                response = SearchResponseSchema(
                    name=person["name"],
                    age=person["age"],
                    occupation=person["occupation"],
                    gender=person["gender"],
                    is_vip=person["is_vip"],
                    vip_score=person["vip_score"],
                    created_at=str(history.__dict__["created_at"]),
                    updated_at=str(history.__dict__["updated_at"]),
                )

               
                responses = await self.vip_sorting([response])
                return responses

        # Instantiate processing class
        process = Process(query)

        # Call main method to get response
        response = await process.main()

        # Save the person to the database on single search case
        if type(query) != list and len(response) > 0:
            for result in response:
                person = await self.save_people_record(result)

                # Add people id to the query
                query["result_id"] = person.id

            # Save query to history
            await HistoryService(self.session).create_history(query, response, user_id)

        # Return results
        
        responses = await self.vip_sorting([response])
        return responses

        

    async def save_people_record(self, person: PeopleCreateSchema) -> People:
        saved_person = People(**person)
        self.session.add(saved_person)
        await self.session.commit()
        await self.session.refresh(saved_person)
        return saved_person
