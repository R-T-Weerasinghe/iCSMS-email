

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/data/integration")
def get_main_dashboard_data():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/data/bi")
def get_bi_data():
    raise HTTPException(status_code=501, detail="Not implemented")
