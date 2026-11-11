from pydantic import BaseModel,Field
class StreamEdit(BaseModel):
    description:str=Field(min_length=8,max_length=1000)
class StreamOutput(BaseModel):
    id:int
    code:str
    name:str
    description:str
    source:str
    lsl:float
    usl:float
    unit:str
    measurement_count:int
