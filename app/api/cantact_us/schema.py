from pydantic import BaseModel, EmailStr


class ContactUsSchema(BaseModel):
    fullname: str
    email: EmailStr
    message: str