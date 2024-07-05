from datetime import datetime, timedelta
import pandas as pd
from fastapi import HTTPException
from pydantic import ValidationError

from api.v2.dependencies.database import collection_issues, collection_inquiries
from api.v2.models.inquiriesModel import InquiryInDB
from api.v2.models.issuesModel import IssueInDB
from api.v2.services.utilityService import build_query, get_first_response_time, get_first_client_msg_time

async def getTimeData(intervalInDaysStart: int, intervalInDaysEnd:int):
    dateTimeStart = datetime.now() - timedelta(days=intervalInDaysStart)
    dateTimeEnd = datetime.now() - timedelta(days=intervalInDaysEnd)

    dateStart = dateTimeStart.replace(hour=0, minute=0, second=0, microsecond=0)
    dateEnd = dateTimeEnd.replace(hour=0, minute=0, second=0, microsecond=0)
    first_response_times = []
    client_msg_times = []

    # FRT for issues
    query = build_query(0, 0, "issue", None, None, None, None, None, dateStart, dateEnd, None)
    issues = list(collection_issues.find(query))
    for issue in issues:
        try:
            issue_obj = IssueInDB(**issue)
        except ValidationError:
            raise HTTPException(status_code=500, detail="Database schema error. Schema mismatch")
        emails = issue_obj.issue_convo_summary_arr
        frt = get_first_response_time(emails)
        client_msg_time = get_first_client_msg_time(emails)
        if frt:
            first_response_times.append(frt)
            client_msg_times.append(client_msg_time)

    # FRT for inquiries
    query = build_query(0, 0, "inquiry", None, None, None, None, None, dateStart, dateEnd, None)
    inquiries = list(collection_inquiries.find(query))
    for inquiry in inquiries:
        try:
            inquiry_obj = InquiryInDB(**inquiry)
        except ValidationError:
            raise HTTPException(status_code=500, detail="Database schema error. Schema mismatch")
        emails = inquiry_obj.inquiry_convo_summary_arr
        frt = get_first_response_time(emails)
        client_msg_time = get_first_client_msg_time(emails)
        if frt:
            first_response_times.append(frt)
            client_msg_times.append(client_msg_time)

    avg_frt = sum(first_response_times) / len(first_response_times) if first_response_times else 0
    # frts
    # client_msg_times
    # only overdue count needed

    df = pd.DataFrame({
        "time": pd.to_datetime(client_msg_times),
        "response_time": first_response_times
    })
    # Set the time as index
    df.set_index("time", inplace=True)
    # Resample data in 5-minute intervals and calculate the mean
    resampled_df = df.resample("5T").mean().dropna()
    # Convert the resampled DataFrame back to lists
    resampled_times = resampled_df.index.strftime("%Y-%m-%dT%H:%M:%S").tolist()
    resampled_first_response_times = resampled_df["response_time"].tolist()
    return {
        "firstResponseTimes": resampled_first_response_times,
        "clientMsgTimes": resampled_times,
        "avgFirstResponseTime": avg_frt,
        "overdueCount": 0,
    }