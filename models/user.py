from sqlalchemy import String
from sqlalchemy.orm import mapped_column,Mapped,relationship
from database import BaseModel

class User(BaseModel):
    '''
    Docstring for User

    'User' entity
    '''

    __tablename__ = 'users'

    id:Mapped[String] = mapped_column(String,primary_key=True)
    username:Mapped[String] = mapped_column(String,unique=True,index=True,nullable=False)
    email:Mapped[String] = mapped_column(String,unique=True,index=True,nullable=False)
    hashed_password:Mapped[String] = mapped_column(String,nullable=False)

    playlists = relationship('Playlist',back_populates='author',cascade='all, delete-orphan')