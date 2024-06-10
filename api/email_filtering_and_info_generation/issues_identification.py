import time
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from dotenv import load_dotenv
import os

from api.email_filtering_and_info_generation.routes import send_inquiry, send_issue, send_suggestion, update_inquiry_status, update_issue_status
from api.email_filtering_and_info_generation.configurations.database import collection_conversations, collection_issues,collection_inquiries
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini LLM with langchain
# llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7,api_key=google_api_key)


# configuring the llm without langchain
genai.configure(api_key=os.getenv('GOOGLE_API_KEY_2'))
# Loading Gemini Pro
model = genai.GenerativeModel('gemini-pro')


async def identify_issues_inquiries_and_checking_status(new_email_msg_array):
    
    # Query to get all thread_ids
    thread_ids = collection_conversations.find({}, {'thread_id': 1, '_id': 0})
    
    # Convert the query result to a list of thread_ids
    thread_id_list = [doc['thread_id'] for doc in thread_ids]  
      
    for new_email_msg in new_email_msg_array:
        
        
        if new_email_msg['thread_id'] not in thread_id_list:
            
            issue_inquiry_identification_script = f""" '{new_email_msg["body"]}' 
                                            If this customer care email is about a customer complaint or reporting an issue (exclude inquiries and suggestions), output 'issue'. 
                                            else If it's an inquiry, output 'inquiry'. 
                                            If it's neither, output 'no'. 
                                            Do not output anything other than 'issue', 'inquiry', or 'no'.
                                            """  
                                        
            #response = llm.invoke(issue_identification_script)
            response = model.generate_content(issue_inquiry_identification_script)
            response.resolve()  
            
            print("issue_inquiry_identification  : " + response.text) 
            
            # if the email of the new thread is an inquiry
            if "inquiry"== response.text:
                time.sleep(10)
                new_email_msg['isInquiry'] = True
                gemini_chat = model.start_chat()
                inquiry_summarizing_script = f""" '{new_email_msg["body"]}' 
                                                Summarize the inquiry mentioned in the above email into one or two lines (minimum one line, maximum two lines).
                                                Do not output anything else other than the summary.
                                                """
                
                responseInq = gemini_chat.send_message(inquiry_summarizing_script)                           
                
                inquiry_summary = responseInq.text
                inquiry_convo_summary = f""" {new_email_msg['sender']}:{new_email_msg['time']}:\n{inquiry_summary}"""
                
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
                
                new_inquiry = {"thread_id": new_email_msg['thread_id'], "recepient_email": new_email_msg['recipient'],"inquiry_summary":inquiry_summary, 
                               "inquiry_convo_summary":inquiry_convo_summary, "status":"ongoing", "inquiry_type":inquiry_type, "products":new_email_msg['products'],
                             "start_time":new_email_msg['time'], "end_time":None, "effectiveness":None, "efficiency":None, "isOverdue":False}
                
                await send_inquiry(new_inquiry)            
            
            # if the email of the new thread is an issue
            if "issue" == response.text:
                time.sleep(10)
                
                
                new_email_msg['isIssue'] = True
                
                gemini_chat = model.start_chat()
                
                issue_summarizing_script = f""" '{new_email_msg["body"]}' 
                                            summarize the issue mentioned in the above email into one or three lines.
                                            (minimum one line. maximum three lines)
                                            Do not outptut anything else other than the summary."""
                                            
                responseIs = gemini_chat.send_message(issue_summarizing_script)                           
                issue_summary = responseIs.text
                issue_convo_summary = f""" {new_email_msg['sender']}:{new_email_msg['time']}:\n{issue_summary}"""
                
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
                
                new_issue = {"thread_id": new_email_msg['thread_id'], "recepient_email": new_email_msg['recipient'], "issue_summary":issue_summary,
                             "issue_convo_summary": issue_convo_summary,"status":"ongoing", "issue_type":issue_type, "products":new_email_msg['products'],
                             "start_time":new_email_msg['time'], "end_time":None, "effectiveness":None, "efficiency":None, "isOverdue":False}
                
                gemini_chat = None
                await send_issue(new_issue)
                
        else:
            
            #---finding cuurent issue thread ids
            issue_thread_ids = collection_issues.find({}, {'thread_id': 1, '_id': 0})
            issue_thread_id_list = [doc['thread_id'] for doc in issue_thread_ids] 
            
            #---finding current inquiry thread ids
            inquiry_thread_ids = collection_inquiries.find({}, {'thread_id': 1, '_id': 0})
            inquiry_thread_id_list = [doc['thread_id'] for doc in inquiry_thread_ids] 
            
            # ---------------------- issues--------------------------------------------------------------------------------

            if new_email_msg['thread_id'] in issue_thread_id_list:
                
                
                time.sleep(15)
                
                convo_summary_doc = collection_issues.find_one({'thread_id': new_email_msg["thread_id"]})
                
                summarize_script = f"""{new_email_msg['body']} summarize the above email body to a minimum word count as possible. output only the summary. don't output anything else. """
                
                summarize_response = model.generate_content(summarize_script)
                summarize_response.resolve()  
                issue_summary = summarize_response.text
                
                print("ongoing issue new part summary" + issue_summary)
                
                new_issue_convo_summary =  convo_summary_doc['issue_convo_summary'] + "\n" + f"""{new_email_msg['sender']}:{new_email_msg['time']}:\n{issue_summary} """
                
                # Initialize the model for a chat
                gemini_chat = model.start_chat()
                
                issue_resolution_checking_script = f""" '{new_issue_convo_summary}'
                                                        This is a summary of a customer care email thread regarding a complaint or issue. Determine if the customer care employee resolved the issue:

                                                        If the employee:
                                                        1. Provided a solution, or
                                                        2. Escalated the complaint to the technical team or some other team, informing the customer they will be contacted soon,

                                                        Output 'yes'. Otherwise, output 'no'. Do not output anything other than 'yes' or 'no'."""
                
                response1 = gemini_chat.send_message(issue_resolution_checking_script)
                
                
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
                    
                    efficiency_of_issue_checking_script = f""" Again consider the previously given issue convo summary and the decide efficiency of the customer care employee based 
                                                                on the following categories. (consider the given datetimes of each message to accurately classify the efficiency category. Carefuly figure out which msgs are sent by customer and which are sent by customer care employee.)
                                                                1.Highly Efficient: The issue was resolved quickly and effectively, demonstrating a high level of effectiveness and timeliness.
                                                                2.Moderately Efficient: The resolution was achieved in a reasonable amount of time with satisfactory effectiveness, though there may be slight room for improvement in either efficiency or effectiveness.
                                                                3.Less Efficient: The resolution process was lengthy or required excessive follow-up, resulting in a delay in solving the issue, although the effectiveness of the resolution may still be satisfactory.
                                                                4.Inefficient: The resolution process was slow and required significant effort or resources, resulting in a prolonged resolution time and potentially lower effectiveness in addressing the customer's issue.

                                                                
                                                                only output the relevant efficiency category. don't output anything else"""
                                                                
                    response3 = gemini_chat.send_message(efficiency_of_issue_checking_script)
                    new_efficiency = response3.text
                    
                    await update_issue_status(new_email_msg['thread_id'], new_issue_convo_summary, "closed", new_email_msg['time'],new_effectiveness,new_efficiency)
                else:
                    
                    await update_issue_status(new_email_msg['thread_id'], new_issue_convo_summary, "ongoing", None,None,None)

                gemini_chat = None
            # ---------------------- iquiry--------------------------------------------------------------------------------
            if new_email_msg['thread_id'] in inquiry_thread_id_list: 
                
                time.sleep(25)
                
                convo_summary_doc = collection_inquiries.find_one({'thread_id': new_email_msg["thread_id"]})
                
                summarize_script = f"""{new_email_msg['body']} summarize the above email body to a minimum word count as possible. output only the summary. don't output anything else. """
                
                summarize_response = model.generate_content(issue_inquiry_identification_script)
                summarize_response.resolve()
                inquiry_summary = summarize_response.text
                
                print("ongoing inquiry new part summary" + inquiry_summary)
                
                new_inquiry_convo_summary =  convo_summary_doc['inquiry_convo_summary'] + "\n" + f"""{new_email_msg['sender']}:{new_email_msg['time']}:\n{inquiry_summary} """
                
                # Initialize the model for the chat
                gemini_chat = model.start_chat()
                
                inquiry_resolution_checking_script = f""" '{new_inquiry_convo_summary}'
                                                        This is a summary of a customer care email thread regarding an inquiry. Determine if the customer care employee has satisfied the inquiry:

                                                        If the employee:
                                                        has provided the relevant needed information to satisfy the customers inquiry.

                                                        Output 'yes'. Otherwise, output 'no'. Do not output anything other than 'yes' or 'no'."""
                
                response1 = gemini_chat.send_message(inquiry_resolution_checking_script)
                
                
                if "yes" == response1.text:
                    
                    effectiveness_of_inquiry_checking_script = f""" consider the previously given inquiry convo summary and the decide effectiveness of the customer care employee based 
                                                                on the following categories.
                                                            1.Highly Effective: The response comprehensively addresses the customer's inquiry with accuracy, clarity, and empathy, resulting in a high level of satisfaction. It provides a solution or resolution that fully resolves the customer's issue and exceeds their expectations.
                                                            2.Moderately Effective: The response adequately addresses the customer's inquiry, demonstrating professionalism and understanding. While there may be room for improvement in certain areas, such as providing additional information or clarification, the customer feels satisfied with the overall outcome.
                                                            3.Minimally Effective: The response partially addresses the customer's inquiry but lacks in certain aspects, such as providing incomplete or generic information. While the customer may appreciate the effort, they are left feeling somewhat dissatisfied or unsure about the resolution.
                                                            4.Ineffective: The response fails to address the customer's inquiry satisfactorily, displaying a lack of understanding or effort on the part of the customer care employee. It may contain errors, inaccuracies, or irrelevant information, leading to significant dissatisfaction and frustration for the customer.
                                                                
                                                                only output the relevant effectiveness category. don't output anything else"""
                    
                    response2 = gemini_chat.send_message(effectiveness_of_inquiry_checking_script)
                    new_effectiveness = response2.text
                    
                    efficiency_of_inquiry_checking_script = f""" Again consider the previously given inquiry convo summary and the decide efficiency of the customer care employee based 
                                                                on the following categories. (consider the given datetimes of each message to accurately classify the efficiency category. Carefuly figure out which msgs are sent by customer and which are sent by customer care employee.)
                                                                1. Highly Efficient: The issue was resolved promptly and effectively, demonstrating a high level of efficiency and timeliness. Responses were sent and received in a timely manner, resulting in a quick resolution of the customer's inquiry.
                                                                2. Moderately Efficient: The resolution was achieved within a reasonable amount of time with satisfactory efficiency. While there may be minor delays or follow-ups in the communication process, the overall resolution time is acceptable, and the customer's inquiry is effectively addressed.
                                                                3. Less Efficient: The resolution process took longer than expected or required excessive follow-up, resulting in a delay in solving the issue. Although the effectiveness of the resolution may still be satisfactory, the prolonged communication time may impact customer satisfaction.
                                                                4. Inefficient: The resolution process was slow and required significant time and effort. There were delays in communication, and the resolution time was prolonged, potentially resulting in lower effectiveness in addressing the customer's issue. This may lead to dissatisfaction on the part of the customer due to the extended response time.

                                                                
                                                                only output the relevant efficiency category. don't output anything else"""
                                                                
                    response3 = gemini_chat.send_message(efficiency_of_inquiry_checking_script)
                    new_efficiency = response3.text
                    
                    await update_inquiry_status(new_email_msg['thread_id'], new_inquiry_convo_summary, "closed", new_email_msg['time'],new_effectiveness,new_efficiency)
                
                else:
                    
                    await update_inquiry_status(new_email_msg['thread_id'], new_inquiry_convo_summary,"ongoing", None, None,None)
                
                gemini_chat = None   
            
            
                    
                
                       