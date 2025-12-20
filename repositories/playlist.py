from sqlalchemy.ext.asyncio import AsyncSession
from .repository import Repository
from models import Playlist

class PlaylistRepository(Repository[Playlist]):

    def __init__(self,db: AsyncSession):
        super().__init__(Playlist, db)
    
    async def _try_get_instance(self, instance: Playlist) -> Playlist | None:
        return await self.get_by_id(instance.id)