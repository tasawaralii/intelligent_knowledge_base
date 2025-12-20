from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    username: str
    email: str
    first_name : str | None = None
    last_name : str | None = None
    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token : str
    token_type: str

class TokenData(BaseModel):
    username : str
    model_config = ConfigDict(from_attributes=True)
