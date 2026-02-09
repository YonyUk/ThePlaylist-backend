import pytest
from unittest.mock import AsyncMock

from models import Playlist
from repositories import PlaylistRepository
from schemas import PlaylistCreateSchema,PlaylistPrivateUpdateSchema,PlaylistUpdateSchema
from services import PlaylistService

# class TestPlaylistService