from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta
import jwt, time
from google.auth import jwt as g_jwt
import aiohttp
from db.models.user import User
from db.db import db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

pwd_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
config_credentials = {
    "SECRET_KEY": "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "REFRESH_SECRET_KEY": "uEGbnTbp9MmQv2imAGgW2XaYMZURq56TMxEGSFPSFphQCVxHsrawxQqP5w2xWmXA",
    "REFRESH_TOKEN_EXPIRE_MINUTES": 43200,  # 30 days
}


authorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid Email or Password",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_hashed_password(password):
    return pwd_crypt.hash(password)


async def verify_password(plain_password, hashed_password):
    return pwd_crypt.verify(plain_password, hashed_password)


async def authenticate_user(
    email, password, session: AsyncSession = Depends(db_session)
):
    user = await session.execute(select(User).where(email=email)).one()
    if user and await verify_password(password, user.password):
        return user
    return False


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode.update({"sub": str(data["id"])})
    encoded_jwt = jwt.encode(
        to_encode,
        config_credentials["SECRET_KEY"],
        algorithm=config_credentials["ALGORITHM"],
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=43200)
    to_encode.update({"exp": expire})
    to_encode.update({"sub": str(data["id"])})
    encoded_jwt = jwt.encode(
        to_encode,
        config_credentials["REFRESH_SECRET_KEY"],
        algorithm=config_credentials["ALGORITHM"],
    )
    return encoded_jwt


async def generate_jwt_pair(id: str, email: str):
    data = {"id": f"{id}", "email": email}
    access_token_expires = timedelta(
        minutes=config_credentials["ACCESS_TOKEN_EXPIRE_MINUTES"]
    )
    access_token = create_access_token(data, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(
        minutes=config_credentials["REFRESH_TOKEN_EXPIRE_MINUTES"]
    )
    refresh_token = create_refresh_token(data, expires_delta=refresh_token_expires)
    return (access_token, refresh_token)


async def verify_google_jwt(jwt_token):

    async with aiohttp.ClientSession() as session:
        """
        This functions verifies a Google JWT Token and gets the user information for the user
        the token belongs to.

        Args:
        jwt_token: str

        Return:
        {
            "nbf":  161803398874,
            "aud": "314159265-pi.apps.googleusercontent.com", // Your server's client ID
            "sub": "3141592653589793238", // The unique ID of the user's Google Account
            "hd": "gmail.com", // If present, the host domain of the user's GSuite email address
            "email": "elisa.g.beckett@gmail.com", // The user's email address
            "email_verified": true, // true, if Google has verified the email address
            "azp": "314159265-pi.apps.googleusercontent.com",
            "name": "Elisa Beckett",
                                        // If present, a URL to user's profile picture
            "picture": "https://lh3.googleusercontent.com/a-/e2718281828459045235360uler",
            "given_name": "Elisa",
            "family_name": "Beckett",
            "iat": 1596474000, // Unix timestamp of the assertion's creation time
            "exp": 1596477600, // Unix timestamp of the assertion's expiration time
            "jti": "abc161803398874def"
        }
        """

        cert_url = "https://www.googleapis.com/oauth2/v1/certs"
        async with session.get(cert_url) as resp:
            google_cert = await resp.json()
            result = g_jwt.decode(jwt_token, google_cert)
            return result


def decodeJWT(token: str, refresh: bool = False) -> dict:
    try:
        if refresh:
            decoded_token = jwt.decode(
                token,
                config_credentials.get("REFRESH_SECRET_KEY"),
                algorithms=[config_credentials.get("ALGORITHM")],
            )
            return decoded_token if decoded_token["exp"] >= time.time() else None
        else:
            decoded_token = jwt.decode(
                token,
                config_credentials.get("SECRET_KEY"),
                algorithms=[config_credentials.get("ALGORITHM")],
            )
            return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}


def refreshJWT(token: str):
    try:
        decoded_token = jwt.decode(
            token,
            config_credentials.get("REFRESH_SECRET_KEY"),
            algorithms=[config_credentials.get("ALGORITHM")],
        )
        print(decoded_token)
        if decoded_token["exp"] >= time.time():
            # create new access token
            access_token_expires = timedelta(
                minutes=config_credentials["ACCESS_TOKEN_EXPIRE_MINUTES"]
            )
            access_token = create_access_token(
                decoded_token, expires_delta=access_token_expires
            )
            return access_token
        else:
            return None
    except:
        return None
