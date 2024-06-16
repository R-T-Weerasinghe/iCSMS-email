
from datetime import datetime, timedelta
import time

from fastapi import HTTPException

from api.email_filtering_and_info_generation.configurations.database import collection_email_msgs, collection_inquiries,collection_issues, collection_conversations



interval = 60
next_time = time.time() + interval


def get_seconds_until(target_hour, target_minute=0):
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target_time < now:
        target_time += timedelta(days=1)
    return (target_time - now).total_seconds()


async def delete_email_msgs(boundaryinWeeks: int):
    
        try:
            # Calculate the threshold date which is one month ago
            one_month_ago = datetime.utcnow() - timedelta(weeks=boundaryinWeeks)

            # Delete documents where start_time is older than one month ago
            result = collection_email_msgs.delete_many({"start_time": {"$lt": one_month_ago}})

            return {"deleted_count": result.deleted_count}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
async def delete_issues_and_inquiries(boundaryinWeeks: int):
    
        try:
            # Calculate the threshold date which is one month ago
            boundary = datetime.utcnow() - timedelta(weeks=boundaryinWeeks)
            # boundary_and_two_weeks_ago = datetime.utcnow() - timedelta(weeks=(boundaryinWeeks+2))

            # Delete documents where start_time is older than one month ago
            resultIssues = collection_issues.delete_many({"end_time": {"$lt": boundary}, "status":"closed"})
        
            resultInquiries = collection_inquiries.delete_many({"end_time": {"$lt": boundary}, "status":"closed"})
            
            resultConvos = collection_conversations.delete_many({"last_updated_time": {"$lt": boundary}})
            

            return {"deleted_issues_count": resultIssues.deleted_count, 
                    "deleted_inquiries_count": resultInquiries.deleted_count,
                    "deleted_convo_summaries_count": resultConvos.deleted_count}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))






async def slide_the_time_window():
    while True:
            now = datetime.now()

            # Check if it's time to run the condition check
            if now.hour == 0 and now.minute == 0:
                await delete_email_msgs(4)
                await delete_issues_and_inquiries(4)
                time.sleep(60)  # Sleep for 1 minute to avoid multiple checks within the same minute

            # Calculate time to sleep until the next check (either 00:00 or 12:00)
            seconds_until_midnight = get_seconds_until(0)

            # Sleep until the next scheduled check time
            sleep_time = seconds_until_midnight
            time.sleep(sleep_time)