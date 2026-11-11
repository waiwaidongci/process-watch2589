from pydantic import BaseModel,Field
class BaselineInput(BaseModel):
    name:str=Field(min_length=2,max_length=120)
    stream_id:int
    sample_count:int=Field(default=80,ge=30,le=190)
