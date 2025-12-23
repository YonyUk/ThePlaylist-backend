from sqlalchemy import Column, ForeignKey, String,Integer,BigInteger,Table
from sqlalchemy.orm import mapped_column,Mapped,relationship
from uuid import uuid4
from database import BaseModel

playlists_tracks = Table(
    'playlists_tracks',
    BaseModel.metadata,
    Column('playlist_id',String,ForeignKey('playlists.id',ondelete='CASCADE'),primary_key=True,index=True),
    Column('track_id',String,ForeignKey('tracks.id',ondelete='CASCADE'),primary_key=True,index=True)
)

class Track(BaseModel):
    '''
    Docstring for Track
    
    Track entity
    '''

    __tablename__ = 'tracks'

    id:Mapped[String] = mapped_column(String,primary_key=True,default=lambda:str(uuid4()))
    file_id:Mapped[String] = mapped_column(String,unique=True,index=True,nullable=False)
    content_hash:Mapped[String] = mapped_column(String,unique=True,nullable=False,index=True)
    name:Mapped[String] = mapped_column(String,nullable=False)
    author_name:Mapped[String] = mapped_column(String,nullable=False)
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