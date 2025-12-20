from sqlalchemy import String,BigInteger,ForeignKey
from sqlalchemy.orm import mapped_column,Mapped,relationship
from uuid import uuid4
from database import BaseModel

class Playlist(BaseModel):
    '''
    Docstring for Playlist

    'Playlist' entity
    '''

    __tablename__ = 'playlists'
    
    id:Mapped[str] = mapped_column(String,primary_key=True,default=lambda:str(uuid4()))
    name:Mapped[str] = mapped_column(String,nullable=False)
    likes:Mapped[int] = mapped_column(BigInteger,default=0)
    dislikes:Mapped[int] = mapped_column(BigInteger,default=0)
    plays:Mapped[int] = mapped_column(BigInteger,default=0)
    description:Mapped[str] = mapped_column(String,nullable=True)
    loves:Mapped[int] = mapped_column(BigInteger,default=0)

    author_id:Mapped[str] = mapped_column(String,ForeignKey('users.id',ondelete='CASCADE'),nullable=False)
    author = relationship('User',back_populates='playlists',lazy='selectin')