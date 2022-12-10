import ast

from db.db import db_session
from db.models.history import History
from db.models.people import People
from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class HistoryService:
    def __init__(self, session: AsyncSession = Depends(db_session)):
        self.session = session


    async def create_history(self, query, response, user_id=None) -> History:
        # Only create history for valid users
        if user_id:

            # Convert query to jsonstring without result_id if it exists
            _query = {k: v for k, v in query.items() if k != "result_id"}
            query["input"] = str(_query)

            # Save query to history
            history = History(**query, result=response, user_id=user_id)
            self.session.add(history)
            await self.session.commit()
            await self.session.refresh(history)

            return history

    async def get_user_history(
        self,
        user_id: str,
        offset: int,
        limit: int,
        start_datetime=None,
        end_datetime=None,
    ):
        statement = select(History).where(History.user_id == user_id)
        
        if start_datetime:
            statement = statement.where(History.created_at >= start_datetime)

        if end_datetime:
            statement = statement.where(History.created_at <= end_datetime)


        user_history = await self.session.execute(
            statement.offset(offset).limit(limit).order_by(History.created_at.desc())
        )
  
        if user_history:
            histories = user_history.scalars().fetchall()

            result = list()
            for item in histories:
                # convert string to dict
                input = eval(item.input)

                # filter off None values
                input = {k: v for k, v in input.items() if v is not None}

                vips = await self.session.execute(select(People).where(People.id == item.result_id))
                vips = dict(vips.scalar())

                # remove unwanted attributes
                dump = ['_sa_instance_state', 'id', 'updated_at', 'created_at']

                for key in dump:
                    vips.pop(key, None)

                # safely return a list version of occupation
                vips['occupation'] = ast.literal_eval(vips['occupation'])

                data = {'history_id': item.id, 'created_at': item.created_at, 'search_input': input, 'result': vips}

                result.append(data.copy())

            return result

        raise HTTPException(
            detail="User has no history", status_code=status.HTTP_404_NOT_FOUND
        )

    async def clear_marked_history(self, history_ids, user_id):
        try:
            _ids = history_ids.dict()['history_ids']
        except:
            raise HTTPException(detail="No history_id passed", status_code=status.HTTP_400_BAD_REQUEST)

        for id in _ids:
            statement = delete(History).where(History.id == id, History.user_id == user_id)
            result = await self.session.execute(statement)
            if result:
                await self.session.commit()
            else:
                raise HTTPException(detail="Invalid History id", status_code=status.HTTP_404_NOT_FOUND)

        return True

    async def clear_all_history(self, user_id):

        statement = delete(History).where(History.user_id == user_id)
        user_history = await self.session.execute(statement)

        if user_history:

            await self.session.commit()

            return True

        else:
            raise HTTPException(detail="User does not have any history", status_code=status.HTTP_404_NOT_FOUND)
