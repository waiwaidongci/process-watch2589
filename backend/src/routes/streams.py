from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..controllers.dependencies import current_user,roles
from ..constants.roles import Role
from ..schemas.stream import StreamEdit,StreamOutput
from ..schemas.measurement import MeasurementOutput
from ..services.stream_service import list_streams,edit_stream
from ..services.measurement_service import list_measurements
router=APIRouter(prefix="/streams",tags=["streams"])
@router.get("",response_model=list[StreamOutput])
def index(db:Session=Depends(get_db),user=Depends(current_user)):return list_streams(db)
@router.get("/{sid}/measurements",response_model=list[MeasurementOutput])
def measurements(sid:int,db:Session=Depends(get_db),user=Depends(current_user)):return list_measurements(db,sid)
@router.patch("/{sid}")
def annotate(sid:int,data:StreamEdit,db:Session=Depends(get_db),user=Depends(roles(Role.ADMIN))):return edit_stream(db,sid,data,user)
