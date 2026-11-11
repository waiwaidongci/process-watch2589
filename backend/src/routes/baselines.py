from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..controllers.dependencies import current_user,roles
from ..constants.roles import Role
from ..schemas.baseline import BaselineInput
from ..services.baseline_service import list_baselines,create_baseline
router=APIRouter(prefix="/baselines",tags=["baselines"])
@router.get("")
def index(db:Session=Depends(get_db),user=Depends(current_user)):return list_baselines(db)
@router.post("",status_code=201)
def create(data:BaselineInput,db:Session=Depends(get_db),user=Depends(roles(Role.ADMIN,Role.ANALYST))):return create_baseline(db,data,user)
