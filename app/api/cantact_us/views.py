from db.db import db_session
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import ContactUsSchema
from .services import ContatctUsService

router = APIRouter()


@router.post("/contact-us")

async def contact_us(
    query: ContactUsSchema,
    session: AsyncSession = Depends(db_session)):
    
    response = await ContatctUsService(session).contact_us_create(query)
    if response:
        return Response(status_code=status.HTTP_200_OK)