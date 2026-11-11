from pydantic import BaseModel
class MeasurementOutput(BaseModel):
    source_key:str
    sequence:int
    measured_at:str
    value:float
