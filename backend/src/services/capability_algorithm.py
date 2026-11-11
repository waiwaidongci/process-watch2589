import math,statistics
from .control_algorithm import validate_values,D2

def capability(values,lsl,usl,stable):
    validate_values(values,3)
    if not(math.isfinite(lsl) and math.isfinite(usl) and lsl<usl):raise ValueError("规格上下限无效")
    mu=statistics.mean(values);sigma=statistics.mean(abs(b-a) for a,b in zip(values,values[1:]))/D2
    if sigma<=1e-12:raise ValueError("监测段移动极差为零，能力指标无法估计")
    cp=(usl-lsl)/(6*sigma);cpk=min(usl-mu,mu-lsl)/(3*sigma)
    return {"cp":cp,"cpk":cpk,"mean":mu,"sigma_within":sigma,"sample_count":len(values),"interpretable":bool(stable and len(values)>=50),"normal_approximation":True,"normality_tested":False,"note":"仅在稳定过程、正态近似与独立采样假设下解释；未做正态检验。" if stable else "稳定性先决条件未满足；以下数值仅保留复算，不作能力结论。"}
