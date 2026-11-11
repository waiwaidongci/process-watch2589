from sqlalchemy import ForeignKey,JSON
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class Baseline(Base):
    __tablename__="baselines"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(unique=True)
    stream_id:Mapped[int]=mapped_column(ForeignKey("measurement_streams.id"))
    sample_count:Mapped[int]
    snapshot:Mapped[dict]=mapped_column(JSON)
    owner:Mapped[str]
    created_at:Mapped[str]=mapped_column(default=now)
