from fastapi import HTTPException
from ..models import Investigation,ControlRun
from ..utils.serialize import record
from ..utils.clock import now
from .audit_service import log

def list_investigations(db):return [record(x) for x in db.query(Investigation).order_by(Investigation.id.desc())]
def create_investigation(db,data,user):
    run=db.get(ControlRun,data.run_id)
    if not run or run.status!="completed":raise HTTPException(409,"只能对已完成运行建立调查")
    row=Investigation(**data.model_dump(),owner=user.name,status="submitted")
    db.add(row);db.flush();log(db,user.email,"investigation.submit",row.id);db.commit();return record(row)
def review_investigation(db,iid,data,user):
    row=db.get(Investigation,iid)
    if not row:raise HTTPException(404,"调查记录不存在")
    if row.status!="submitted":raise HTTPException(409,"已复核记录不能重复审批")
    row.status=data.status;row.review_note=data.review_note;row.reviewer=user.name;row.reviewed_at=now()
    log(db,user.email,"investigation."+data.status,row.id);db.commit();return record(row)
