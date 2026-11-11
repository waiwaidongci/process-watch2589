from sqlalchemy import ForeignKey,JSON
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class ControlRun(Base):
    __tablename__="control_runs"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]
    baseline_id:Mapped[int]=mapped_column(ForeignKey("baselines.id"))
    smoothing:Mapped[float]=mapped_column(default=.2)
    ewma_l:Mapped[float]=mapped_column(default=3.)
    status:Mapped[str]=mapped_column(default="queued")
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    error:Mapped[str]=mapped_column(default="")
    owner:Mapped[str]
    created_at:Mapped[str]=mapped_column(default=now)
