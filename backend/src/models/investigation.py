from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from ..config.database import Base
from ..utils.clock import now
class Investigation(Base):
    __tablename__="investigations"
    id:Mapped[int]=mapped_column(primary_key=True)
    run_id:Mapped[int]=mapped_column(ForeignKey("control_runs.id"))
    title:Mapped[str]
    finding:Mapped[str]
    action:Mapped[str]
    status:Mapped[str]=mapped_column(default="submitted")
    owner:Mapped[str]
    reviewer:Mapped[str]=mapped_column(default="")
    review_note:Mapped[str]=mapped_column(default="")
    created_at:Mapped[str]=mapped_column(default=now)
    reviewed_at:Mapped[str]=mapped_column(default="")
