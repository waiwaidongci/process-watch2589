import random,json
from datetime import datetime,timedelta,timezone
from src.config.database import SessionLocal,Base,engine
from src.models import User,MeasurementStream,Measurement,Baseline,ControlRun,Investigation
from src.utils.security import hash_password
from src.services.control_algorithm import freeze_measurements,analyze_process

def seed():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        for role,name in [("admin","程砚 · 质量负责人"),("analyst","沈微 · 工艺分析师"),("viewer","顾远 · 工艺观察员")]:
            email=role+"@qingzhen.demo"
            if not db.query(User).filter_by(email=email).first():db.add(User(email=email,name=name,role=role,password_hash=hash_password("Qingzhen2026!")))
        for idx,name,mu,sd in [(1,"底涂稳定参考",20.,.22),(2,"面涂低位参考",19.65,.28),(3,"热喷涂漂移观察",20.,.22),(4,"试制波动观察",20.1,.48)]:
            code=f"T-{idx:02}";stream=db.query(MeasurementStream).filter_by(code=code).first()
            if not stream:
                stream=MeasurementStream(code=code,name=name,description="每10分钟采样一次的合成膜厚，按测量序号保留时间顺序；规格18–22μm。",source="qt-coating-202611.csv",lsl=18.,usl=22.,unit="μm")
                db.add(stream);db.flush()
            rng=random.Random({1:605,2:502,3:802,4:504}[idx]);existing=set(x[0] for x in db.query(Measurement.source_key).filter_by(stream_id=stream.id))
            for i in range(1,241):
                value=round(rng.gauss(mu,sd)+(0.85 if idx==3 and i>150 else 0),4);key=f"{code}-{i:04}"
                if key not in existing:db.add(Measurement(stream_id=stream.id,source_key=key,sequence=i,measured_at=(datetime(2026,11,1,tzinfo=timezone.utc)+timedelta(minutes=10*(i-1))).isoformat(),value=value))
            db.flush();bname=code+" · 前80点冻结基线";baseline=db.query(Baseline).filter_by(name=bname).first()
            rows=db.query(Measurement).filter_by(stream_id=stream.id).order_by(Measurement.sequence).all()
            if not baseline:
                baseline=Baseline(name=bname,stream_id=stream.id,sample_count=80,snapshot=freeze_measurements(rows,80),owner="沈微 · 工艺分析师")
                db.add(baseline);db.flush()
            if idx in [1,3]:
                rname=code+" · 首次过程观察";run=db.query(ControlRun).filter_by(name=rname).first()
                if not run:
                    run=ControlRun(name=rname,baseline_id=baseline.id,smoothing=.2,ewma_l=3.,status="completed",result=analyze_process(rows,baseline,stream,.2,3.),owner="沈微 · 工艺分析师")
                    db.add(run);db.flush()
                    if idx==1:db.add(Investigation(run_id=run.id,title="T-01基准复核档案",finding="已核对控制界限和规格界限来源，统计结果保留完整假设说明。",action="继续独立采样并按周复查，不将单次能力值作为保证。",status="approved",owner="沈微 · 工艺分析师",reviewer="程砚 · 质量负责人",review_note="批准此研究记录归档，能力解释仍以稳定及正态近似为前提。",reviewed_at=datetime.now(timezone.utc).isoformat()))
        db.commit();print(json.dumps({m.__tablename__:db.query(m).count() for m in [User,MeasurementStream,Measurement,Baseline,ControlRun,Investigation]},ensure_ascii=False))
if __name__=="__main__":seed()
