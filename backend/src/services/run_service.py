import csv,io
from redis import Redis
from fastapi import HTTPException
from ..config.settings import REDIS_URL
from ..models import ControlRun,Baseline,Investigation
from ..utils.serialize import record
from .audit_service import log
queue=Redis.from_url(REDIS_URL,decode_responses=True)
def list_runs(db):return [record(r) for r in db.query(ControlRun).order_by(ControlRun.id.desc())]
def get_run(db,rid):
    row=db.get(ControlRun,rid)
    if not row:raise HTTPException(404,"运行不存在")
    return row

def create_run(db,data,user):
    if not db.get(Baseline,data.baseline_id):raise HTTPException(404,"基线不存在")
    row=ControlRun(**data.model_dump(),owner=user.name)
    db.add(row);db.flush();log(db,user.email,"control.enqueue",row.id);db.commit()
    try:queue.rpush("process:jobs",row.id)
    except Exception:
        row.status="failed";row.error="队列不可用，请重新提交";db.commit();raise HTTPException(503,row.error)
    return record(row)
def export_run(db,rid):
    row=get_run(db,rid)
    if row.status!="completed":raise HTTPException(409,"运行尚未完成")
    if not db.query(Investigation).filter_by(run_id=rid,status="approved").first():raise HTTPException(403,"调查尚未经负责人批准，不能导出")
    out=io.StringIO();writer=csv.writer(out)
    writer.writerow(['sequence','time','thickness','moving_range','ewma','ewma_lower','ewma_upper','signals','input_hash'])
    for p in row.result['points']:writer.writerow([p['sequence'],p['measured_at'],p['value'],p['moving_range'],p['ewma'],p['ewma_lower'],p['ewma_upper'],'|'.join(p['signals']),row.result['input_hash']])
    return out.getvalue()
