from pydantic import BaseModel,Field
class RunInput(BaseModel):
    name:str=Field(min_length=2,max_length=120)
    baseline_id:int
    smoothing:float=Field(default=.2,gt=0,le=1,allow_inf_nan=False)
    ewma_l:float=Field(default=3.,ge=1,le=5,allow_inf_nan=False)
