from fastapi import HTTPException
from ..models import MeasurementStream,Measurement
from ..utils.serialize import record
from .audit_service import log

def list_streams(db):return [dict(record(s),measurement_count=db.query(Measurement).filter_by(stream_id=s.id).count()) for s in db.query(MeasurementStream).order_by(MeasurementStream.code)]
def get_stream(db,sid):
    row=db.get(MeasurementStream,sid)
    if not row:raise HTTPException(404,"测量流不存在")
    return row

def edit_stream(db,sid,data,user):
    row=get_stream(db,sid);row.description=data.description;log(db,user.email,"stream.annotate",row.code);db.commit();return record(row)
