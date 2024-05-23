import functools

import jwt
from fastapi import HTTPException, Security, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime,timedelta

class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'watasino0721womitekudasai'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='签名已过期')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="非法token")

    def jwt_required(self, func):
        @functools.wraps(func)
        async def wrapper(request: Request,*args, **kwargs):
            token = request.headers.get('Authorization')
            if token:
                try:
                    auth_token = self.decode_token(token)
                except HTTPException as e:
                    raise e
                except Exception as e:
                    raise e
            else:
                raise HTTPException(status_code=401, detail="未授权")
            return await func(request,*args, **kwargs)
        return wrapper




