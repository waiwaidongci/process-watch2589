from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
class MeasurementStream(Base):
    __tablename__="measurement_streams"
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(unique=True)
    name:Mapped[str]
    description:Mapped[str]
    source:Mapped[str]
    lsl:Mapped[float]
    usl:Mapped[float]
    unit:Mapped[str]=mapped_column(default="μm")
