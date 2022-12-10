from datetime import date, datetime
from typing import Union

from api.history.schemas import CreateHistorySchema
from api.search.schemas import SearchResponseSchema
from api.user.views import auth_handler
from db.db import db_session
from db.models.history import History as history
from db.models.people import People as people
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi_pagination import Page, Params, paginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


from .schemas import HistoryIDSchema
from .services import HistoryService

router = APIRouter()


@router.get("/top-search", status_code=status.HTTP_200_OK)
async def top_searched_stars(
    date_sort: str = None,
    ascending_sort: bool = None,
    user_id=Depends(auth_handler.auth_wrapper),
    session: AsyncSession = Depends(db_session)
):
    """
    A function that handles sorting of user's search history
    and return the top searched VIP.
    The top searched VIP is based on the VIP score of the searched VIPs

    args:
        token: a Bearer Token as an header
        date_sort:(format- YYYY-MM-DD)-an optional argument. if being passed,
        the database would be filtered to return results that match the query param
    Raise:
        HTTP_401_UNAUTHORIZED - if valid token not supplied
        HTTP_403_FORBIDDEN - if valid token has expired
    Response:
        {
        "name": "cristiano ronaldo",
        "age": 37,
        "gender": "male",
        "occupation": null,
        "vip_score": 80,
        "timstamp": "2022-11-02"
        }
    url-format-sample: https://domain/api/history/top-search?sort_by=2022-11-02
    """
    history_list = []
    vip_profile = {}

    query = (
        select(
            [
                history.created_at,
                people.name,
                people.age,
                people.gender,
                people.occupation,
                people.vip_score,
            ]
        )
        .where(history.user_id == user_id)
        .join(people)
    )


    if date_sort:
        # split the date sort argument and convert from strng to datetime.date format
        try:
            new_time = date_sort.split("-")
            new_time = [int(time) for time in new_time]
            new_time = date(year=new_time[0], month=new_time[1], day=new_time[2])
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format"
            )
        query = query.filter(func.date(history.created_at) <= new_time).limit(30)
        user_history = await session.execute(query)
        # sort the Vip date sort option either by ascending or descending as user specifies
        if ascending_sort and ascending_sort == True:
            user_history = sorted(
                user_history, key=lambda user: (datetime.date(user[0]), user[5])
            )
        else:
            user_history = sorted(
                user_history,
                key=lambda user: (datetime.date(user[0]), user[5]),
                reverse=True,
            )
    else:
        query = query.order_by(people.vip_score.desc()).limit(30)
        user_history = await session.execute(query)

    #     # run the query if sort by argument is passed
    for user in user_history:
        vip_profile["name"] = user[1]
        vip_profile["age"] = user[2]
        vip_profile["gender"] = user[3]
        vip_profile["occupation"] = user[4]
        vip_profile["vip_score"] = user[5]
        vip_profile["timestamp"] = user[0].strftime("%Y-%m-%d")
        if int(user[5]) >= 90:
            vip_profile["category"] = "gold"
        if int(user[5]) >= 55 < 90:
            vip_profile["category"] = "silver"
        if int(user[5]) < 55:
            vip_profile["category"] = "bronze"
        history_list.append(vip_profile.copy())

    return history_list


@router.get("/") 
async def get_past_requests(
    user_id=Depends(auth_handler.auth_wrapper),
    params: Params = Depends(),
    start_datetime: Union[datetime, None] = None, 
    end_datetime: Union[datetime, None] = None,
    session: AsyncSession = Depends(db_session),
):
    

    """

    Get User Past Searches Queries all the search request made by a specific User.

    Note :
    Authorization Token is required to get the current user

    Date Time Format = 2022-12-01 19:44:02.248483

    """
    
    history_service = HistoryService(session=session)
    histories = await history_service.get_user_history(

        user_id=user_id,
        offset=0,
        limit=1000,
        start_datetime=start_datetime,
        end_datetime=end_datetime,

    )
    return paginate(histories, params=params)


@router.delete("/delete/selected")
async def delete_history(
        history_ids: HistoryIDSchema,
        user_id=Depends(auth_handler.auth_wrapper),
        session: AsyncSession = Depends(db_session)):

    """
    Selected history should be passed as a list/array of UUID/GUID objects

    where each UUID represents the id of the history object

    Example data:

        {
            "history_ids": [

                "23d092ad-f307-46e5-8993-4b8a9d4f5a33",

                "60c6437d-fd40-4885-a609-05e004383471"
                
            ]
        }
    """
    success = await HistoryService(session).clear_marked_history(history_ids, user_id)
    if success:
        return Response(status_code=status.HTTP_202_ACCEPTED)


@router.delete("/delete/all")
async def clear_all_history(user_id=Depends(auth_handler.auth_wrapper), session: AsyncSession = Depends(db_session)):

    """
    Clears all search history of the user whose api-key is sent with the request
    """

    success = await HistoryService(session).clear_all_history(user_id)

    if success:
        return Response(status_code=status.HTTP_202_ACCEPTED)

