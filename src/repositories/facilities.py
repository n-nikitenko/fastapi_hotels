from models import FacilityOrm
from repositories.base import BaseRepository
from schemas import Facility


class FacilityRepository(BaseRepository):
    _model = FacilityOrm
    _schema = Facility