from ..models import Measurement
from ..utils.serialize import record
from .stream_service import get_stream

def list_measurements(db,sid):
    get_stream(db,sid)
    return [record(x) for x in db.query(Measurement).filter_by(stream_id=sid).order_by(Measurement.sequence)]
