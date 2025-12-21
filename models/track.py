from sqlalchemy import Column, ForeignKey, String,Float,Table
from sqlalchemy.orm import mapped_column,Mapped,relationship
from uuid import uuid4
from database import BaseModel

playlists_tracks = Table(
    'playlists_tracks',
    BaseModel.metadata,
    Column('playlist_id',String,ForeignKey('playlists.id',ondelete='CASCADE'),primary_key=True),
    Column('track_id',String,ForeignKey('tracks.id',ondelete='CASCADE'),primary_key=True)
)

class Track(BaseModel):
    '''
    Docstring for Track
    
    Track entity
    '''

    __tablename__ = 'tracks'

    id:Mapped[String] = mapped_column(String,primary_key=True,default=lambda:str(uuid4()))
    name:Mapped[String] = mapped_column(String,nullable=False)
    author_name:Mapped[String] = mapped_column(String,nullable=False)
    size:Mapped[Float] = mapped_column(Float,nullable=False)

    playlists = relationship(
        'Playlist',
        back_populates='tracks',
        lazy='selectin',
        secondary=playlists_tracks
    )