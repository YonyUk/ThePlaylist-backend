from sqlalchemy import String,BigInteger,ForeignKey
from sqlalchemy.orm import mapped_column,Mapped,relationship
from database import BaseModel

class Playlist(BaseModel):
    '''
    Docstring for Playlist

    'Playlist' entity
    '''

    __tablename__ = 'playlists'
    
    id:Mapped[String] = mapped_column(String,primary_key=True)
    name:Mapped[String] = mapped_column(String,nullable=False)
    likes:Mapped[BigInteger] = mapped_column(BigInteger,default=0)
    dislikes:Mapped[BigInteger] = mapped_column(BigInteger,default=0)
    plays:Mapped[BigInteger] = mapped_column(BigInteger,default=0)
    description:Mapped[String] = mapped_column(String,nullable=True)
    loves:Mapped[BigInteger] = mapped_column(BigInteger,default=0)

    author_id:Mapped[String] = mapped_column(String,ForeignKey('users.id',ondelete='CASCADE'),nullable=False,index=True)
    author = relationship('User',back_populates='playlists',lazy='selectin')

    tracks = relationship(
        'Track',
        back_populates='playlists',
        lazy='selectin',
        secondary='playlists_tracks'
    )