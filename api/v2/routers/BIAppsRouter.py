from fastapi import APIRouter
from api.v2.models.BIAPPModel import BIAppResponse
from api.v2.services import BIAppService as services
router = APIRouter()


@router.get("/dashboard/business_insights", response_model=BIAppResponse)
async def generate_bi_response(intervalInDaysStart: int, intervalInDaysEnd:int):
    
    result: BIAppResponse = await services.generate_bi_response(intervalInDaysStart, intervalInDaysEnd)
    print("BI Response",result)
    return result