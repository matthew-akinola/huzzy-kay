from fastapi import APIRouter, HTTPException, Depends
from .schemas import SearchResponseSchema, SearchParamsSchema, SearchListSchema
from .services import SearchService
from typing import List
from db.db import db_session
from sqlmodel.ext.asyncio.session import AsyncSession
from api.user.services import UserService

router = APIRouter()

auth_handler = UserService()


@router.get("/", response_model=List[SearchResponseSchema])
async def search_vips(
    name: str,
    gender: str = None,
    occupation: str = None,
    age: int = None,
    email: str = None,
    session: AsyncSession = Depends(db_session),
    user_id = Depends(auth_handler.api_key_wrapper)
):
    try:
        search_service = SearchService(session=session)
        resp = await search_service.search(
            {
                "name": name,
                "gender": gender,
                "occupation": occupation,
                "age": age,
                "email": email,
            }, user_id=user_id
        )

        return resp

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while validating VIP",
        )


@router.post("/search-many")
async def search_vip_list(
    params: SearchListSchema, 
    user_id = Depends(auth_handler.api_key_wrapper),
    session: AsyncSession = Depends(db_session)):

    try:
        search_result = []
        data = [i.__dict__ for i in params.data]
        for search_info in data:
            # for every dictionary in the data list
            # add a user id as the authenticated user's ID
            search_service = SearchService(session=session)
            resp = await search_service.search(search_info, user_id=user_id)
            search_result.append(resp)
        return search_result

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while validating VIP",
        )
