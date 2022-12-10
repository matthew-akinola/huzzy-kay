from passlib.context import CryptContext
from api.user.schemas import Signup, Login, GoogleSchema, Email
from db.db import db_session
from db.models.user import User
from db.models.api import ApiKey
from fastapi import Depends, HTTPException, status, Security, Header
from api.user.authentication import generate_jwt_pair
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

X_API_KEY = APIKeyHeader(name="X-API-KEY", auto_error=False)
pwd_crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
config_credentials = {
    "SECRET_KEY": "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 10080,  # 7 days
}
security = HTTPBearer()

authorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid Email or Password",
    headers={"WWW-Authenticate": "Bearer"},
)


class UserService:
    def __init__(self, session: AsyncSession = Depends(db_session)):
        self.session = session

    def get_password_hash(self, password):
        return pwd_crypt.hash(password)

    async def verify_password(self, plain_password, hashed_password):
        return pwd_crypt.verify(plain_password, hashed_password)

    def encode_token(self, data: dict, expires_delta=None):
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        data["exp"] = expire
        encoded_jwt = jwt.encode(
            data,
            config_credentials["SECRET_KEY"],
            algorithm=config_credentials["ALGORITHM"],
        )
        return encoded_jwt

    def decode_token(self, token):
        try:
            payload = jwt.decode(
                token,
                config_credentials["SECRET_KEY"],
                algorithms=config_credentials["ALGORITHM"],
            )
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    async def api_key_wrapper(
        self,
        x_api_key: str = Depends(X_API_KEY),
        session: AsyncSession = Depends(db_session),
    ):
        statement = select(ApiKey).where(ApiKey.api_key == x_api_key)
        if x_api_key:
            key = await session.execute(statement)
            if key:
                key = key.scalars().first()
                return key.user_id
        return None

    async def create_user(self, user: Signup) -> User:
        if (
            user.first_name == ""
            or user.last_name == ""
            or user.email == ""
            or user.password == ""
        ):
            raise HTTPException(
                status_code=401, detail="please all fields are required"
            )

        statement = select(User).where(User.email == user.email)
        userdetails = await self.session.execute(statement)
        userdetails = userdetails.scalars().first()
        if userdetails:
            raise HTTPException(
                status_code=400, detail="email already exist, please try a new one"
            )
        else:
            password = self.get_password_hash(user.password)
            user.password = password
            new_user = User(**user.dict())
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)

            access_token, refresh_token = await generate_jwt_pair(
                new_user.id, new_user.email
            )

            user_ = new_user.dict()
            user_.pop("password")
            user_.pop("created_at")
            user_.pop("updated_at")

            data = {
                "user": user_,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

            return self.success("Registration was sucessful", data)

    async def login_user(self, user: Login):
        if user.email == "" or user.password == "":
            raise HTTPException(
                status_code=401, detail="email and password is required"
            )

        userdetails = await self.authenticate_user(user.email, user.password)
        if not userdetails:
            raise HTTPException(status_code=401, detail="Invalid Email or Password")
        access_token, refresh_token = await generate_jwt_pair(
            userdetails.id, userdetails.email
        )
        data = {
            "user": userdetails,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        return self.success("Login was successful", data)

    def success(self, message, data):
        return {"status": "success", "message": message, "data": data}

    async def authenticate_user(self, email, password):
        try:
            statement = select(User).where(User.email == email)
            user = await self.session.execute(statement)
            user = user.scalars().first()
            if user and await self.verify_password(password, user.password):
                return user
        except:
            return False

    async def get_api_key(self, user_id, password):
        query = select(User).where(User.id == user_id)
        user = await self.session.execute(query)
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="Not Authenticated")
        check_two = self.verify_password(password, user.password)
        if not check_two:
            raise HTTPException(status_code=401, detail="Invalid password supplied")

        statement = select(ApiKey).where(ApiKey.user_id == user.id)
        key = await self.session.execute(statement)
        key = key.scalars().first()
        if not key:
            key = await self.create_api_key(user)
        data = {"user": user, "key": key.api_key}
        return self.success("Key was returned successfully", data)

    async def get_api_key(self, user):
        statement = select(ApiKey).where(ApiKey.user_id == user.id)
        key = await self.session.execute(statement)
        key = key.scalars().first()
        if key is None:
            key = ApiKey(user_id=user.id)
            self.session.add(key)
            await self.session.commit()
            await self.session.refresh(key)
        return key

    async def verify_api_key(self, key):
        statement = select(ApiKey).where(ApiKey.api_key == key)
        apiKey = await self.session.execute(statement)
        apiKey = apiKey.scalars().first()
        if not apiKey:
            raise HTTPException(status_code=401, detail="Invalid Key")

        userStatement = select(User).where(User.id == apiKey.user_id)
        user = await self.session.execute(userStatement)
        user = user.scalars().first()
        if user:
            data = {"api_key": apiKey.api_key}
        return self.success("Api Key was verified successfully", data)

    async def change_password(self, user_id, cur_password, new_password):
        if cur_password == "" or new_password == "":
            raise HTTPException(status_code=401, detail="password is required")

        statement = select(User).where(User.id == user_id)
        user = await self.session.execute(statement)
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User does not exist")

        verify_password = pwd_crypt.verify(cur_password, user.password)
        if not verify_password:
            raise HTTPException(
                status_code=401, detail="Current password does not match"
            )

        check_password = pwd_crypt.verify(new_password, user.password)
        if not check_password:
            _password = self.get_password_hash(new_password)
            user.password = _password
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return self.success("Password was updated sucessfully", user)
        else:
            raise HTTPException(
                status_code=401,
                detail="You have used this password before, try a new one",
            )

    async def get_logged_user(self, user_id):
        statement = select(User).where(User.id == user_id)
        user = await self.session.execute(statement)
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User does not exist")

        return self.success("User returned successfully", user)

    async def google_create_user(self, user: GoogleSchema):
        statement = select(User).where(User.email == user.email)
        userdetails = await self.session.execute(statement)
        userdetails = userdetails.scalars().first()
        if userdetails:
            raise HTTPException(
                status_code=400, detail="email already exist, please try a new one"
            )

        userdetails.first_name = user.name
        userdetails.last_name = user.googleId
        userdetails.email = user.email
        userdetails.password = user.accessToken
        new_user = User(**user.dict())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return self.success("Registration was sucessful", new_user)

    async def google_authenticate(self, user):
        """
        Generates access_token for a google verified user

        Args:
        user: User Model Instance

        Return:
        access_token: generated access token
        """

        if not user:
            raise authorized_exception
        return self.create_token(user)

    async def create_token(self, user):
        access_token, refresh_token = await generate_jwt_pair(user.id, user.email)

        return access_token, refresh_token

    async def find_by_email(self, email):
        """
        Find a user by Email

        Args:
        email: user email address

        Return:
            User: Found User Object
                or
            None
        """
        try:
            statement = select(User).where(User.email == email)
            user = await self.session.execute(statement)
            found_user = user.scalars().first()
            return found_user
        except Exception as e:
            print(e)
            return None

    async def email_verify(self, email):
        if email == "":
            raise HTTPException(status_code=401, detail="email is required")

        statement = select(User).where(User.email == email)
        user = await self.session.execute(statement)
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="email does not exist")

        return self.success("Proceed to reset password", user.email)

    async def password_reset(self, user: Login):
        if user.email == "" or user.password == "":
            raise HTTPException(
                status_code=401, detail="email and password is required"
            )

        statement = select(User).where(User.email == user.email)
        userdetails = await self.session.execute(statement)
        userdetails = userdetails.scalars().first()
        if not userdetails:
            raise HTTPException(status_code=401, detail="User does not exist")

        check_password = pwd_crypt.verify(user.password, userdetails.password)
        if not check_password:
            _password = self.get_password_hash(user.password)
            userdetails.password = _password
            self.session.add(userdetails)
            await self.session.commit()
            await self.session.refresh(userdetails)
            return self.success("Password was reset sucessfully", userdetails)
        else:
            raise HTTPException(
                status_code=401,
                detail="You have used this password before, try a new one",
            )

    async def get_single_user(self, user_id):
        if user_id == "":
            raise HTTPException(status_code=401, detail="user_id is required")

        statement = select(User).where(User.id == user_id)
        userdetails = await self.session.execute(statement)
        userdetails = userdetails.scalars().first()

        if not userdetails:
            raise HTTPException(status_code=401, detail="user does not exist")

        return self.success("Returned user's details successfully", userdetails)

    async def update_user(self, user_id, first_name, last_name):
        statement = select(User).where(User.id == user_id)
        user = await self.session.execute(statement)
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User does not exist")

        user.first_name = first_name
        user.last_name = last_name
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return self.success("User Records updated sucessfully", user)

    async def find_by_id(self, id):
        """
        Find a user by Email

        Args:
        email: user email address

        Return:
            User: Found User Object
                or
            None
        """
        statement = select(User).where(User.id == id)
        try:
            user = await self.session.execute(statement)
            found_user = user.scalars().first()
            return found_user
        except Exception as e:
            print(e)
            return None
