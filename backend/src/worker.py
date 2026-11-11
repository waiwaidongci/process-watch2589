import time,json,traceback
from pathlib import Path
from .config.database import Base,engine,SessionLocal
from .models import ControlRun,Baseline,MeasurementStream,Measurement
from .constants.status import RunStatus
from .services.run_service import queue
from .services.control_algorithm import analyze_process
from .services.audit_service import log
Base.metadata.create_all(engine);Path("/artifacts").mkdir(exist_ok=True)
while True:
    Path("/artifacts/heartbeat").write_text(str(time.time()))
    job=queue.blpop("process:jobs",timeout=2)
    if not job:continue
    with SessionLocal() as db:
        run=db.get(ControlRun,int(job[1]))
        if not run or run.status!=RunStatus.QUEUED:continue
        run.status=RunStatus.RUNNING;db.commit()
        try:
            baseline=db.get(Baseline,run.baseline_id);stream=db.get(MeasurementStream,baseline.stream_id)
            rows=db.query(Measurement).filter_by(stream_id=stream.id).order_by(Measurement.sequence).all()
            run.result=analyze_process(rows,baseline,stream,run.smoothing,run.ewma_l);run.status=RunStatus.COMPLETED
            Path(f"/artifacts/run-{run.id}.json").write_text(json.dumps(run.result,ensure_ascii=False))
            log(db,"worker","control.completed",run.id)
        except Exception as e:run.status=RunStatus.FAILED;run.error=str(e);traceback.print_exc()
        db.commit()
