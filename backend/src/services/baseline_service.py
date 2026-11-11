from fastapi import HTTPException
from ..models import Baseline,Measurement
from ..utils.serialize import record
from .stream_service import get_stream
from .control_algorithm import freeze_measurements
from .audit_service import log

def list_baselines(db):return [record(b) for b in db.query(Baseline).order_by(Baseline.id.desc())]
def create_baseline(db,data,user):
    get_stream(db,data.stream_id)
    if db.query(Baseline).filter_by(name=data.name).first():raise HTTPException(409,"基线名称已存在")
    rows=db.query(Measurement).filter_by(stream_id=data.stream_id).order_by(Measurement.sequence).all()
    if len(rows)-data.sample_count<50:raise HTTPException(422,"至少保留50个后续监测点")
    try:snapshot=freeze_measurements(rows,data.sample_count)
    except ValueError as e:raise HTTPException(422,str(e))
    row=Baseline(**data.model_dump(),snapshot=snapshot,owner=user.name)
    db.add(row);db.flush();log(db,user.email,"baseline.freeze",row.id);db.commit();return record(row)
