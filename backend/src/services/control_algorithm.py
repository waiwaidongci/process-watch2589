"""Individuals/MR Phase-I estimation and Phase-II EWMA. Constants: d2=1.128, D4=3.267."""
import math,statistics
from ..utils.fingerprint import fingerprint,measurement_record
D2=1.128
D4=3.267

def validate_values(values,min_count=5):
    if len(values)<min_count:raise ValueError(f"至少需要{min_count}个测量点")
    if any(type(v) not in (int,float) or abs(v)>1e9 or not math.isfinite(v) for v in values):raise ValueError("测量值必须为有限数字")
    if max(abs(v) for v in values)>1e9:raise ValueError("测量值超出支持范围")

def estimate_baseline(values):
    validate_values(values)
    mr=[abs(b-a) for a,b in zip(values,values[1:])]
    mean=statistics.mean(values);mrbar=statistics.mean(mr);sigma=mrbar/D2
    if sigma<=1e-12:raise ValueError("移动极差为零，无法建立统计控制界限")
    ilow,ihigh=mean-3*sigma,mean+3*sigma
    i_flags=[i+1 for i,x in enumerate(values) if x<ilow or x>ihigh]
    mr_flags=[i+2 for i,x in enumerate(mr) if x>D4*mrbar]
    return {"mean":mean,"mrbar":mrbar,"sigma":sigma,"i_lower":ilow,"i_upper":ihigh,"mr_upper":D4*mrbar,"i_signals":i_flags,"mr_signals":mr_flags,"stable":not(i_flags or mr_flags)}

def freeze_measurements(rows,sample_count):
    ordered=sorted(rows,key=lambda r:r.sequence)
    if len({r.sequence for r in ordered})!=len(ordered):raise ValueError("测量序号重复")
    if not 5<=sample_count<=len(ordered)-3:raise ValueError("基线范围不足或没有后续监测点")
    chosen=ordered[:sample_count];points=[measurement_record(x) for x in chosen]
    return {"points":points,"statistics":estimate_baseline([x.value for x in chosen]),"input_hash":fingerprint(points),"end_sequence":chosen[-1].sequence}

def monitor_values(values,baseline,smoothing=.2,ewma_l=3.,previous=None):
    validate_values(values,3)
    if not math.isfinite(smoothing) or not 0<smoothing<=1:raise ValueError("EWMA lambda必须在(0,1]内")
    if not math.isfinite(ewma_l) or not 1<=ewma_l<=5:raise ValueError("EWMA L必须在[1,5]内")
    mu,sigma,mrbar=baseline['mean'],baseline['sigma'],baseline['mrbar']
    if not all(math.isfinite(v) for v in [mu,sigma,mrbar]) or sigma<=1e-12:raise ValueError("基线参数无效")
    z=mu;points=[];previous=mu if previous is None else previous
    for i,x in enumerate(values,1):
        mr=abs(x-previous);previous=x;z=smoothing*x+(1-smoothing)*z
        width=ewma_l*sigma*math.sqrt(smoothing/(2-smoothing)*(1-(1-smoothing)**(2*i)))
        lower,upper=mu-width,mu+width
        flags=[]
        if x<mu-3*sigma or x>mu+3*sigma:flags.append('individual')
        if mr>D4*mrbar:flags.append('moving_range')
        if z<lower or z>upper:flags.append('ewma')
        points.append({"value":x,"moving_range":mr,"ewma":z,"ewma_lower":lower,"ewma_upper":upper,"signals":flags})
    return points

def analyze_process(rows,baseline,stream,smoothing=.2,ewma_l=3.):
    ordered=sorted(rows,key=lambda x:x.sequence)
    if len({x.sequence for x in ordered})!=len(ordered):raise ValueError("测量序号重复")
    validate_values([x.value for x in ordered])
    snapshot=baseline.snapshot
    monitored=[x for x in ordered if x.sequence>snapshot['end_sequence']]
    if len(monitored)<50:raise ValueError("能力研究至少需要50个后续独立监测点")
    if not (math.isfinite(stream.lsl) and math.isfinite(stream.usl) and stream.lsl<stream.usl):raise ValueError("规格下限必须小于上限且均为有限数字")
    control=monitor_values([x.value for x in monitored],snapshot['statistics'],smoothing,ewma_l,snapshot['points'][-1]['value'])
    points=[dict(measurement_record(row),**point) for row,point in zip(monitored,control)]
    signals=[{"sequence":p['sequence'],"kind":kind,"value":p['ewma'] if kind=='ewma' else p['moving_range'] if kind=='moving_range' else p['value']} for p in points for kind in p['signals']]
    from .capability_algorithm import capability
    stable=snapshot['statistics']['stable'] and not signals
    cap=capability([x.value for x in monitored],stream.lsl,stream.usl,stable)
    stream_data={"id":stream.id,"code":stream.code,"name":stream.name,"lsl":stream.lsl,"usl":stream.usl,"unit":stream.unit}
    input_data={"method":"imr-ewma-capability-v1","stream":stream_data,"source":[measurement_record(x) for x in ordered],"baseline":snapshot,"smoothing":smoothing,"ewma_l":ewma_l}
    source_baseline=[measurement_record(x) for x in ordered[:baseline.sample_count]]
    return {"stream":stream_data,"baseline":{"id":baseline.id,"name":baseline.name,"sample_count":baseline.sample_count,**snapshot},"points":points,"signals":signals,"signal_counts":{k:sum(s['kind']==k for s in signals) for k in ['individual','moving_range','ewma']},"monitor_count":len(monitored),"stable":stable,"capability":cap,"smoothing":smoothing,"ewma_l":ewma_l,"baseline_source_changed":fingerprint(source_baseline)!=snapshot['input_hash'],"input_hash":fingerprint(input_data),"method_version":"imr-ewma-capability-v1","interpretation":"未见本工具三类越界信号；能力值仍以正态近似和独立性为前提" if stable else "过程存在稳定性信号，Cp/Cpk不得用于宣称过程能力","assumptions":"正态近似、按时间独立采样；未检验正态性或自相关。控制界限由冻结基线估计，规格18–22等为外部要求，两者不同。"}
