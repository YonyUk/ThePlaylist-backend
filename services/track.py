from repositories import TrackRepository
from models import Track
from schemas import TrackUploadSchema,TrackUpdateSchema,TrackSchema
from .service import Service

class TrackService(Service[
    Track,
    TrackRepository,
    TrackUploadSchema,
    TrackUpdateSchema,
    TrackSchema
]):
    def __init__(self, repository: TrackRepository, exclude_fields: set = set(), exclude_unset: bool = True):
        super().__init__(Track, TrackSchema,repository, exclude_fields, exclude_unset)