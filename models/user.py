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
    
    tracks_likes = relationship(
        'Track',
        back_populates='users_likes',
        secondary='tracks_likes'
    )

    tracks_dislikes = relationship(
        'Track',
        back_populates='users_dislikes',
        secondary='tracks_dislikes'
    )

    tracks_loves = relationship(
        'Track',
        back_populates='users_loves',
        secondary='tracks_loves'
    )

    playlists_likes = relationship(
        'Playlist',
        back_populates='users_likes',
        secondary='playlists_likes'
    )

    playlists_dislikes = relationship(
        'Playlist',
        back_populates='users_dislikes',
        secondary='playlists_dislikes'
    )

    playlists_loves = relationship(
        'Playlist',
        back_populates='users_loves',
        secondary='playlists_loves'
    )