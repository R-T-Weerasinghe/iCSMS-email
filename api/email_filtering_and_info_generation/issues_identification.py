import time
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from api.email_filtering_and_info_generation.models import InquiryInDB, IssueInDB
from dotenv import load_dotenv
import os

from external_services.aws_comprehend.sentiment_analysis import analyze_sentiment
from utils.helpers import scale_score

from api.email_filtering_and_info_generation.services import get_all_reading_accounts, send_inquiry, send_issue, send_suggestion, update_inquiry_status, update_issue_status
from api.email_filtering_and_info_generation.configurations.database import collection_conversations, collection_issues,collection_inquiries
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY_2")

# Initialize Gemini LLM with langchain
# llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)


# configuring the llm without langchain
genai.configure(api_key=os.getenv('GOOGLE_API_KEY_2'))
# Loading Gemini Pro
model = genai.GenerativeModel('gemini-pro')



async def identify_issues_inquiries_and_checking_status(new_email_msg_array):
    
    # # Query to get all thread_ids
    # thread_ids = collection_conversations.find({}, {'thread_id': 1, '_id': 0})
    # # Convert the query result to a list of thread_ids
    # thread_id_list = [doc['thread_id'] for doc in thread_ids]
    
    reading_email_accounts = await get_all_reading_accounts()
    

    i = 0
  
      
    for new_email_msg in new_email_msg_array:
        
        if(i%3==0):
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY_5'))
            # Loading Gemini Pro
            model = genai.GenerativeModel('gemini-pro')
        elif(i%3==1): 
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY_6'))
            # Loading Gemini Pro
            model = genai.GenerativeModel('gemini-pro')
        else:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY_4'))
            # Loading Gemini Pro
            model = genai.GenerativeModel('gemini-pro')
            
        i = i+1 
        
        issue_document = collection_issues.find_one({'thread_id': new_email_msg["thread_id"]})
        inquiry_document = collection_inquiries.find_one({'thread_id': new_email_msg["thread_id"]})
        
        if not issue_document and not inquiry_document:
            
            # checking whether the first email of the thread came from a client
            if new_email_msg['sender'] not in reading_email_accounts:
            
                issue_inquiry_identification_script = f""" '{new_email_msg["body"]}' 
                                                If this customer care email is about a customer complaint or reporting an issue (exclude inquiries and suggestions), output 'issue'. 
                                                else If it's an inquiry, output 'inquiry'. 
                                                If it's neither, output 'no'. 
                                                Do not output anything other than 'issue', 'inquiry', or 'no'.
                                                """  
                                            
                #response = llm.invoke(issue_identification_script)
                response = model.generate_content(issue_inquiry_identification_script)
                response.resolve()  
                
                time.sleep(3)
                
                print("issue_inquiry_identification  : " + response.text) 
                
                # if the email of the new thread is an inquiry
                if "inquiry"== response.text:
                   
                    new_email_msg['isInquiry'] = True
                    gemini_chat = model.start_chat()
                    inquiry_summarizing_script = f""" '{new_email_msg["body"]}' 
                                                    Summarize the inquiry mentioned in the above email into one or two lines (minimum one line, maximum two lines).
                                                    Do not output anything else other than the summary.
                                                    """
                    
                    responseInq = gemini_chat.send_message(inquiry_summarizing_script)                           
                    
                    inquiry_summary = responseInq.text
                    
                    time.sleep(3)
                    inquiry_convo_summary_dict =  {
                                                "sender":new_email_msg['sender'], 
                                                "sender_type":"client",
                                                "time":new_email_msg['time'],
                                                "message":inquiry_summary}
                    
                    inquiry_convo_summary_arr = []
                    inquiry_convo_summary_arr.append(inquiry_convo_summary_dict)
                    
                    sentiment_score = round(scale_score(analyze_sentiment(inquiry_summary)), 2)
                    
                    inquiry_type_identification_script = f""" tell me to which of the following inquiry types does the above inquiry falls into
                                                        1.Product Information
                                                        2.Pricing and Discounts
                                                        3.Shipping and Delivery
                                                        4.Warranty and Guarantees
                                                        5.Account Information
                                                        6.Technical Support
                                                        7.Policies and Procedures
                                                        8.Payment Methods
                                                        Only output the inquiry type. Do not output anything else."""
                    
                    responseInqt = gemini_chat.send_message(inquiry_type_identification_script)                           
                    inquiry_type = responseInqt.text
                    
                    print("inquiry type  : " + inquiry_type) 
                    
                    
                    new_inquiry = InquiryInDB(
                                thread_id = new_email_msg['thread_id'], 
                                thread_subject = new_email_msg['subject'],
                                recepient_email= new_email_msg['recipient'],
                                sender_email=new_email_msg['sender'],
                                inquiry_summary=inquiry_summary, 
                                inquiry_convo_summary_arr=inquiry_convo_summary_arr, 
                                status="ongoing", 
                                ongoing_status ="new", 
                                inquiry_type=inquiry_type, 
                                products=new_email_msg['products'],
                                sentiment_score = sentiment_score,
                                start_time = new_email_msg['time'], updated_time=new_email_msg['time'] , end_time=None, 
                                effectiveness=None, efficiency=None, 
                                isOverdue=False)

                    
                    await send_inquiry(new_inquiry)            
                
                # if the email of the new thread is an issue
                if "issue" == response.text:
                    
                    new_email_msg["isIssue"] = True
                    
                    new_email_msg['isIssue'] = True
                    
                    gemini_chat = model.start_chat()
                    
                    issue_summarizing_script = f""" '{new_email_msg["body"]}' 
                                                summarize the issue mentioned in the above email into one or three lines.
                                                (minimum one line. maximum three lines)
                                                Do not outptut anything else other than the summary."""
                                                
                    responseIs = gemini_chat.send_message(issue_summarizing_script)                           
                    issue_summary = responseIs.text
                    time.sleep(3)
                    
                    issue_convo_summary_dict = {
                                                "sender":new_email_msg['sender'], 
                                                "sender_type":"client",
                                                "time":new_email_msg['time'],
                                                "message":issue_summary}
                    issue_convo_summary_arr = []
                    issue_convo_summary_arr.append(issue_convo_summary_dict)
                    
                    sentiment_score = round(scale_score(analyze_sentiment(issue_summary)), 2)
                    
                    issue_type_identification_script = f""" tell me to which of the following issue types does the above issue falls into
                                                        1.Order Issues
                                                        2.Billing and Payment Problems
                                                        3.Account Issues
                                                        4.Product or Service Complaints
                                                        5.Technical Issues
                                                        6.Warranty and Repair Issues
                                                        7.Subscription Problems
                                                        8.Return and Exchange Problems
                                                        Only output the issue type (Exact issue type as given above). Do not output anything else."""
                    
                    responseIst = gemini_chat.send_message(issue_type_identification_script)                           
                    issue_type = responseIst.text
                    
                    print("issue type  : " + issue_type) 
                    time.sleep(15)
                    
                    new_issue = IssueInDB(
                                thread_id= new_email_msg['thread_id'], 
                                thread_subject = new_email_msg['subject'],
                                recepient_email= new_email_msg['recipient'],
                                sender_email=new_email_msg['sender'], 
                                issue_summary=issue_summary,
                                issue_convo_summary_arr= issue_convo_summary_arr,
                                status="ongoing", 
                                ongoing_status="new", 
                                issue_type=issue_type, 
                                products=new_email_msg['products'],
                                sentiment_score = sentiment_score,
                                start_time=new_email_msg['time'], updated_time=new_email_msg['time'], end_time=None, 
                                effectiveness=None, efficiency=None, 
                                isOverdue =False)
                    
                    
                    gemini_chat = None
                    await send_issue(new_issue)
                
        else:
            

            
            # ---------------------- issues--------------------------------------------------------------------------------

            if issue_document:
                
                new_email_msg["isIssue"] = True
                
                
                # identifying sender type
                if new_email_msg['sender'] not in reading_email_accounts:
                    sender_type = "client"
                else:
                    sender_type = "company"
                    
                current_issue_doc = issue_document
                
                summarize_script = f"""{new_email_msg['body']} summarize the above email body to a minimum word count as possible. output only the summary. don't output anything else. """
                
                summarize_response = model.generate_content(summarize_script)
                summarize_response.resolve()  
                issue_summary = summarize_response.text
                time.sleep(3)
                
                print("ongoing issue new part summary" + issue_summary)
                
                current_issue_convo_summary_arr = current_issue_doc['issue_convo_summary_arr']
                new_issue_convo_summary_dict = {
                                            "sender":new_email_msg['sender'], 
                                            "sender_type":sender_type,
                                            "time":new_email_msg['time'],
                                            "message":issue_summary}
                
                current_issue_convo_summary_arr.append(new_issue_convo_summary_dict)
                new_issue_convo_summary_arr = current_issue_convo_summary_arr
                
                issue_convo_summary_text_form = ""
                
                for dict in new_issue_convo_summary_arr:
                    issue_convo_summary_text_form = issue_convo_summary_text_form + "\n" + f"""{dict['sender']}:{dict['time']}:\n{dict['message']} """
                
                
                
                new_ongoing_status = ""
                if new_email_msg['sender'] in reading_email_accounts: 
                    new_ongoing_status = "waiting"
                else:
                    new_ongoing_status = "update"
                
                sentiment_score = round(scale_score(analyze_sentiment(issue_convo_summary_text_form)), 2)
                
                # Initialize the model for a chat
                gemini_chat = model.start_chat()
                
                issue_resolution_checking_script = f""" '{issue_convo_summary_text_form}'
                                                        This is a summary of a customer care email thread regarding a complaint or issue. Determine if the customer care employee resolved the issue:

                                                        If the employee:
                                                        1. Provided a solution, or
                                                        2. Escalated the complaint to the technical team or some other team, informing the customer they will be contacted soon,

                                                        Output 'yes'. Otherwise, output 'no'. Do not output anything other than 'yes' or 'no'."""
                
                response1 = gemini_chat.send_message(issue_resolution_checking_script)
                
                time.sleep(3)
                
                if "yes" == response1.text:
                                        
                    effectivenes_of_issue_checking_script = f""" consider the above given issue convo summary and the decide effectiveness of the customer care employee based 
                                                                on the following categories.
                                                                1.Highly Effective: The resolution comprehensively addresses the customer's issue with accuracy, courtesy, and empathy, resulting in a high level of customer satisfaction.
                                                                2.Moderately Effective: The resolution adequately addresses the customer's issue, demonstrating professionalism and understanding, although there may be minor areas for improvement.
                                                                3.Minimally Effective: The resolution partially addresses the customer's issue but lacks in certain aspects such as accuracy, empathy, or effectiveness of communication, resulting in some level of dissatisfaction.
                                                                4.Ineffective: The resolution fails to address the customer's issue satisfactorily, displaying a lack of understanding, professionalism, or appropriate action, leading to significant dissatisfaction.
                                                                
                                                                only output the relevant effectiveness category. don't output anything else"""
                    
                    response2 = gemini_chat.send_message(effectivenes_of_issue_checking_script)
                    new_effectiveness = response2.text
                    time.sleep(3)
                    efficiency_of_issue_checking_script = f""" Again consider the previously given issue convo summary and the decide efficiency of the customer care employee based 
                                                                on the following categories. (consider the given datetimes of each message to accurately classify the efficiency category. Carefuly figure out which msgs are sent by customer and which are sent by customer care employee.)
                                                                1.Highly Efficient: The issue was resolved quickly and effectively, demonstrating a high level of effectiveness and timeliness.
                                                                2.Moderately Efficient: The resolution was achieved in a reasonable amount of time with satisfactory effectiveness, though there may be slight room for improvement in either efficiency or effectiveness.
                                                                3.Less Efficient: The resolution process was lengthy or required excessive follow-up, resulting in a delay in solving the issue, although the effectiveness of the resolution may still be satisfactory.
                                                                4.Inefficient: The resolution process was slow and required significant effort or resources, resulting in a prolonged resolution time and potentially lower effectiveness in addressing the customer's issue.

                                                                
                                                                only output the relevant efficiency category. don't output anything else"""
                                                                
                    response3 = gemini_chat.send_message(efficiency_of_issue_checking_script)
                    new_efficiency = response3.text
                    
                    await update_issue_status(new_email_msg['thread_id'], new_issue_convo_summary_arr, new_email_msg['time'],"closed", None, sentiment_score, new_email_msg['time'],new_effectiveness,new_efficiency)
                else:
                    
                    await update_issue_status(new_email_msg['thread_id'], new_issue_convo_summary_arr, new_email_msg['time'],"ongoing", new_ongoing_status, sentiment_score, None,None,None)

                gemini_chat = None
            # ---------------------- iquiry--------------------------------------------------------------------------------
            if inquiry_document: 
                new_email_msg['isInquiry'] = True
                
                if new_email_msg['sender'] not in reading_email_accounts:
                    sender_type = "client"
                else:
                    sender_type = "company"
                
                convo_summary_doc = inquiry_document
                
                summarize_script = f"""{new_email_msg['body']} summarize the above email body to a minimum word count as possible. output only the summary. don't output anything else. """
                
                summarize_response = model.generate_content(summarize_script)
                summarize_response.resolve()
                inquiry_summary = summarize_response.text
                time.sleep(3)
                
                print("ongoing inquiry new part summary" + inquiry_summary)
                
                current_inquiry_convo_summary_arr = convo_summary_doc['inquiry_convo_summary_arr']
                new_inquiry_convo_summary_dict = {
                                            "sender":new_email_msg['sender'],
                                            "sender_type":sender_type, 
                                            "time":new_email_msg['time'],
                                            "message":inquiry_summary}
                
                current_inquiry_convo_summary_arr.append(new_inquiry_convo_summary_dict)
                new_inquiry_convo_summary_arr = current_inquiry_convo_summary_arr
                
                inquiry_convo_summary_text_form = ""
                
                for dict in new_inquiry_convo_summary_arr:
                    inquiry_convo_summary_text_form = inquiry_convo_summary_text_form + "\n" + f"""{dict['sender']}:{dict['time']}:\n{dict['message']} """
                
                new_ongoing_status = ""
                if new_email_msg['sender'] in reading_email_accounts: 
                    new_ongoing_status = "waiting"
                else:
                    new_ongoing_status = "update"
                
                sentiment_score = round(scale_score(analyze_sentiment(inquiry_convo_summary_text_form)), 2)
                    
                # Initialize the model for the chat
                gemini_chat = model.start_chat()
                
                inquiry_resolution_checking_script = f""" '{inquiry_convo_summary_text_form}'
                                                        This is a summary of a customer care email thread regarding an inquiry. Determine if the customer care employee has satisfied the inquiry:

                                                        If the employee:
                                                        has provided the relevant needed information to satisfy the customers inquiry.

                                                        Output 'yes'. Otherwise, output 'no'. Do not output anything other than 'yes' or 'no'."""
                
                response1 = gemini_chat.send_message(inquiry_resolution_checking_script)
                time.sleep(3)
                
                if "yes" == response1.text:
                    
                    effectiveness_of_inquiry_checking_script = f""" consider the previously given inquiry convo summary and the decide effectiveness of the customer care employee based 
                                                                on the following categories.
                                                            1.Highly Effective: The response comprehensively addresses the customer's inquiry with accuracy, clarity, and empathy, resulting in a high level of satisfaction. It provides a solution or resolution that fully resolves the customer's inquiry and exceeds their expectations.
                                                            2.Moderately Effective: The response adequately addresses the customer's inquiry, demonstrating professionalism and understanding. While there may be room for improvement in certain areas, such as providing additional information or clarification, the customer feels satisfied with the overall outcome.
                                                            3.Minimally Effective: The response partially addresses the customer's inquiry but lacks in certain aspects, such as providing incomplete or generic information. While the customer may appreciate the effort, they are left feeling somewhat dissatisfied or unsure about the resolution.
                                                            4.Ineffective: The response fails to address the customer's inquiry satisfactorily, displaying a lack of understanding or effort on the part of the customer care employee. It may contain errors, inaccuracies, or irrelevant information, leading to significant dissatisfaction and frustration for the customer.
                                                                
                                                                only output the relevant effectiveness category. don't output anything else"""
                    
                    response2 = gemini_chat.send_message(effectiveness_of_inquiry_checking_script)
                    new_effectiveness = response2.text
                    time.sleep(3)
                    efficiency_of_inquiry_checking_script = f""" Again consider the previously given inquiry convo summary and the decide efficiency of the customer care employee based 
                                                                on the following categories. (consider the given datetimes of each message to accurately classify the efficiency category. Carefuly figure out which msgs are sent by customer and which are sent by customer care employee.)
                                                                1. Highly Efficient: The inquiry was resolved promptly and effectively, demonstrating a high level of efficiency and timeliness. Responses were sent and received in a timely manner, resulting in a quick resolution of the customer's inquiry.
                                                                2. Moderately Efficient: The resolution was achieved within a reasonable amount of time with satisfactory efficiency. While there may be minor delays or follow-ups in the communication process, the overall resolution time is acceptable, and the customer's inquiry is effectively addressed.
                                                                3. Less Efficient: The resolution process took longer than expected or required excessive follow-up, resulting in a delay in solving the inquiry. Although the effectiveness of the resolution may still be satisfactory, the prolonged communication time may impact customer satisfaction.
                                                                4. Inefficient: The resolution process was slow and required significant time and effort. There were delays in communication, and the resolution time was prolonged, potentially resulting in lower effectiveness in addressing the customer's inquiry. This may lead to dissatisfaction on the part of the customer due to the extended response time.

                                                                
                                                                only output the relevant efficiency category. don't output anything else"""
                                                                
                    response3 = gemini_chat.send_message(efficiency_of_inquiry_checking_script)
                    new_efficiency = response3.text
                    
                    await update_inquiry_status(new_email_msg['thread_id'], new_inquiry_convo_summary_arr, new_email_msg['time'], "closed", None, sentiment_score,new_email_msg['time'],new_effectiveness,new_efficiency)
                
                else:
                    
                    await update_inquiry_status(new_email_msg['thread_id'], new_inquiry_convo_summary_arr, new_email_msg['time'],"ongoing", new_ongoing_status, sentiment_score, None, None,None)
                
                gemini_chat = None   
            
            
                    
                
                       