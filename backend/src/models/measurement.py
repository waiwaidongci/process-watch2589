from sqlalchemy import ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
class Measurement(Base):
    __tablename__="measurements"
    __table_args__=(UniqueConstraint("stream_id","sequence"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    stream_id:Mapped[int]=mapped_column(ForeignKey("measurement_streams.id"))
    source_key:Mapped[str]=mapped_column(unique=True)
    sequence:Mapped[int]
    measured_at:Mapped[str]
    value:Mapped[float]
