from db.db import db_session
from db.models.contact_us import ContactUs
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import ContactUsSchema


class ContatctUsService:
    def __init__(self, session: AsyncSession = Depends(db_session)):
        self.session = session


    async def contact_us_create(self, query: ContactUsSchema) -> ContactUs:
      
        if (
            query.fullname == ""
            or query.email == ""
            or query.message == ""
        ):
            raise HTTPException(
                status_code=401, detail="please all fields are required"
            )
         
        if query:
            # Save query to C
            contact_us = ContactUs(**query.dict())
            self.session.add(contact_us)
            await self.session.commit()
            await self.session.refresh(contact_us)
            return contact_us
