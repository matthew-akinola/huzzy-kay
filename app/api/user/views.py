from fastapi import APIRouter, Depends, HTTPException, status
from db.db import db_session

from api.user.schemas import (
    Signup,
    Login,
    APIKey,
    PasswordChange,
    GoogleAuthSchema,
    Email,
    Update,
)
from db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from api.user.authentication import refreshJWT, verify_google_jwt, decodeJWT
from fastapi.security import OAuth2PasswordBearer
from api.user.services import UserService
from .auth_bearer import JWTBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_handler = UserService()


@router.post("/signup", status_code=201)
async def create_user(user: Signup, session: AsyncSession = Depends(db_session)):
    user_service = UserService(session=session)
    new_user = await user_service.create_user(user)
    return new_user


@router.post("/login")
async def login(user: Login, session: AsyncSession = Depends(db_session)):
    user_service = UserService(session=session)
    res = await user_service.login_user(user)
    user = res["data"]["user"]
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "access_token": res["data"]["access_token"],
        "refresh_token": res["data"]["refresh_token"],
        "token_type": "bearer",
    }


@router.post("/verify/")
async def verify_api_key(key: APIKey, session: AsyncSession = Depends(db_session)):
    user_service = UserService(session=session)
    key = await user_service.verify_api_key(key)
    return key


@router.post("/change_password", status_code=201)
async def change_user_password(
    form_data: PasswordChange,
    session: AsyncSession = Depends(db_session),
    user_id=Depends(auth_handler.auth_wrapper),
):
    user_service = UserService(session=session)
    res = await user_service.change_password(
        user_id, form_data.cur_password, form_data.new_password
    )
    return res


@router.post("/google-auth/")
async def google_auth(
    data: GoogleAuthSchema, session: AsyncSession = Depends(db_session)
):
    """

    This endpoint authenticates Users using their Google JWT.
    It can also be used for registering users using thier Google JWT.

    """

    jwt_token = data.jwt_token
    try:
        g_user = await verify_google_jwt(jwt_token)
        user_service = UserService(session=session)
        result = await user_service.find_by_email(g_user.get("email"))
        if result:
            access_token = await user_service.google_authenticate(result)
            return {
                "user": result.dict(),
                "access_token": access_token,
            }
        else:
            g_user = {
                "first_name": g_user.get("given_name"),
                "last_name": g_user.get("family_name"),
                "email": g_user.get("email"),
                "password": g_user.get("sub"),
            }
            new_user = Signup(**g_user)
            user = await user_service.create_user(new_user)
            user = user["data"]
            return user
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or Expired Google JWT",
        )


@router.get("/get_api_keys")
async def get_api_keys(
    jwt_token: str = Depends(JWTBearer()), session: AsyncSession = Depends(db_session)
):
    payload = decodeJWT(jwt_token)
    user_id = payload.get("sub")
    user_service = UserService(session=session)
    user = await user_service.find_by_id(user_id)
    api_key = await user_service.get_api_key(user)
    return api_key.dict()


@router.get("/logged_in_user", status_code=200)
async def loggedin_user(
    session: AsyncSession = Depends(db_session),
    user_id=Depends(auth_handler.auth_wrapper),
):
    user_service = UserService(session=session)
    res = await user_service.get_logged_user(user_id)
    return res


@router.post("/verify_email")
async def verify_email(user: Email, session: AsyncSession = Depends(db_session)):
    user_service = UserService(session=session)
    response = await user_service.email_verify(user.email)
    return response


@router.post("/reset_password")
async def reset_password(user: Login, session: AsyncSession = Depends(db_session)):
    user_service = UserService(session=session)
    response = await user_service.password_reset(user)
    return response


@router.get("/get_single_user", status_code=200)
async def get_user(user_id, session: AsyncSession = Depends(db_session)):
    user_service = UserService(session=session)
    res = await user_service.get_single_user(user_id)
    return res


@router.patch("/update_user_profie", status_code=201)
async def update_user_profile(
    form_data: Update,
    session: AsyncSession = Depends(db_session),
    user_id=Depends(auth_handler.auth_wrapper),
):
    user_service = UserService(session=session)
    res = await user_service.update_user(
        user_id, form_data.first_name, form_data.last_name
    )
    return res


@router.post("/refresh_token")
async def refresh_token(
    refresh_token: str = Depends(JWTBearer(refresh=True)),
):
    access_token = refreshJWT(refresh_token)
    return {"access_token": access_token}
