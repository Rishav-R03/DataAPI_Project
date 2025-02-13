from pydantic import BaseModel

class user(BaseModel):
    username:str
    email:str
    password:str

class loginReq(BaseModel):
    email:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    username:str | None = None
