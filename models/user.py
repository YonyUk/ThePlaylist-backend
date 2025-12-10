from sqlalchemy import String
from sqlalchemy.orm import mapped_column,Mapped
from uuid import uuid4
from database import BaseModel

class User(BaseModel):
    '''
    Docstring for User

    'User' entity
    '''

    __tablename__ = 'users'

    id:Mapped[String] = mapped_column(String,primary_key=True,default=lambda:str(uuid4()))
    username:Mapped[String] = mapped_column(String,nullable=False)
    email:Mapped[String] = mapped_column(String,unique=True,index=True,nullable=False)
    hashed_password:Mapped[String] = mapped_column(String,nullable=False)