from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bearer_scheme = HTTPBearer()


def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})

    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: HTTPAuthorizationCredentials, credentials_exception):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=ALGORITHM)
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
        return user_id

    except JWTError:
        raise credentials_exception


# verifies if the token is correct
def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    user_id = verify_access_token(token, credentials_exception)
    return int(user_id)