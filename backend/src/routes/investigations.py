from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..controllers.dependencies import current_user,roles
from ..constants.roles import Role
from ..schemas.investigation import InvestigationInput,ReviewInput
from ..services.investigation_service import list_investigations,create_investigation,review_investigation
router=APIRouter(prefix="/investigations",tags=["investigations"])
@router.get("")
def index(db:Session=Depends(get_db),user=Depends(current_user)):return list_investigations(db)
@router.post("",status_code=201)
def create(data:InvestigationInput,db:Session=Depends(get_db),user=Depends(roles(Role.ADMIN,Role.ANALYST))):return create_investigation(db,data,user)
@router.patch("/{iid}/review")
def review(iid:int,data:ReviewInput,db:Session=Depends(get_db),user=Depends(roles(Role.ADMIN))):return review_investigation(db,iid,data,user)
