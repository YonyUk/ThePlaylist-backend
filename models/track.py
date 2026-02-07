from sqlalchemy import Column, ForeignKey, String,Integer,BigInteger,Table
from sqlalchemy.orm import mapped_column,Mapped,relationship
from database import BaseModel

playlists_tracks = Table(
    'playlists_tracks',
    BaseModel.metadata,
    Column('playlist_id',String,ForeignKey('playlists.id',ondelete='CASCADE'),primary_key=True,index=True),
    Column('track_id',String,ForeignKey('tracks.id',ondelete='CASCADE'),primary_key=True,index=True)
)

tracks_likes = Table(
    'tracks_likes',
    BaseModel.metadata,
    Column('track_id',String,ForeignKey('tracks.id',ondelete='CASCADE'),primary_key=True,index=True),
    Column('user_id',String,ForeignKey('users.id',ondelete='CASCADE'),primary_key=True,index=True)
)

tracks_dislikes = Table(
    'tracks_dislikes',
    BaseModel.metadata,
    Column('track_id',String,ForeignKey('tracks.id',ondelete='CASCADE'),primary_key=True,index=True),
    Column('user_id',String,ForeignKey('users.id',ondelete='CASCADE'),primary_key=True,index=True)
)

tracks_loves = Table(
    'tracks_loves',
    BaseModel.metadata,
    Column('track_id',String,ForeignKey('tracks.id',ondelete='CASCADE'),primary_key=True,index=True),
    Column('user_id',String,ForeignKey('users.id',ondelete='CASCADE'),primary_key=True,index=True)
)

class Track(BaseModel):
    '''
    Docstring for Track
    
    Track entity
    '''

    __tablename__ = 'tracks'

    id:Mapped[String] = mapped_column(String,primary_key=True)
    file_id:Mapped[String] = mapped_column(String,unique=True,index=True,nullable=False)
    content_hash:Mapped[String] = mapped_column(String,unique=True,nullable=False,index=True)
    name:Mapped[String] = mapped_column(String,nullable=False,index=True)
    author_name:Mapped[String] = mapped_column(String,nullable=False,index=True)
    size:Mapped[Integer] = mapped_column(Integer,nullable=False)
    likes:Mapped[BigInteger] = mapped_column(BigInteger,default=0)
    dislikes:Mapped[BigInteger] = mapped_column(BigInteger,default=0)
    plays:Mapped[BigInteger] = mapped_column(BigInteger,default=0)
    loves:Mapped[BigInteger] = mapped_column(BigInteger,default=0)
    uploaded_by:Mapped[String] = mapped_column(String,ForeignKey('users.id',ondelete='CASCADE'),nullable=False,index=True)

    playlists = relationship(
        'Playlist',
        back_populates='tracks',
        lazy='selectin',
        secondary=playlists_tracks
    )

    users_likes = relationship(
        'User',
        back_populates='tracks_likes',
        secondary=tracks_likes
    )

    users_dislikes = relationship(
        'User',
        back_populates='tracks_dislikes',
        secondary=tracks_dislikes
    )

    users_loves = relationship(
        'User',
        back_populates='tracks_loves',
        secondary=tracks_loves
    )