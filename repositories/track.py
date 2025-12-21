from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .repository import Repository
from models import Track,Playlist

class TrackRepository(Repository):

    def __init__(self,db: AsyncSession):
        super().__init__(Track, db)
    
    async def _try_get_instance(self, instance: Track) -> Track | None:
        return await self.get_by_id(str(instance.id))