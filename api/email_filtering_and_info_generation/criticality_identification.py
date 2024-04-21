from langchain_google_genai import ChatGoogleGenerativeAI
from api.email_filtering_and_info_generation.config import API_KEY  
import google.generativeai as genai
from dotenv import load_dotenv
import os

# os.environ['GOOGLE_API_KEY'] = API_KEY

# Load environment variables from .env file
load_dotenv()
# google_api_key = os.getenv("GOOGLE_API_KEY")

# # Check if the value is not None before setting the environment variable
# if google_api_key is not None:
#     os.environ['GOOGLE_API_KEY'] = google_api_key
    
# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

# genai.configure(api_key=API_KEY)
# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content("What is the meaning of life?")
# print(response.text)

def identify_criticality(new_email_msg_array):
        
    ciricality_categorization = """High Criticality:
    Description: These emails represent urgent issues that require immediate attention. They could result in financial loss, reputational damage, or significant customer dissatisfaction if not addressed promptly.
    Examples:Account security breaches
    Order cancellations impacting critical deadlines
    Major product malfunctions posing safety hazards
    Public complaints from influential figures
    Medium Criticality:
    Description: These emails involve important issues that need to be addressed within a reasonable timeframe. They might impact customer satisfaction or loyalty, but don't pose an immediate threat.
    Examples:Product defects or functionality issues impacting usability
    Delayed deliveries causing inconvenience
    Billing errors or discrepancies
    Strong dissatisfaction with customer service interactions (previous attempts made)
    Low Criticality:
    Description: These emails address non-urgent inquiries or requests that can be handled within a standard timeframe. They might involve general questions, product feedback, or minor inconveniences.
    Examples:Questions about product features or usage
    Requests for order information or tracking updates
    Feedback on customer experience (positive or negative)
    Minor order issues (e.g., missing instructions)
    Informational:
    Description: These emails don't require a specific response from customer service. They might be for unsubscribing, providing compliments, or general information sharing.
    Examples:Unsubscribe requests
    Positive customer testimonials
    Product registration confirmations
    """

    # email_body = """
    # I am writing to express my deep dissatisfaction and frustration regarding my recent purchase experience with [Company Name]. I believe it is crucial for you to address this matter immediately.
    # [Describe the issue you encountered in detail, including any relevant order or account numbers, dates of purchase, and specific problems you faced.]
    # Despite my anticipation of a seamless and satisfactory transaction, I encountered [specific issue(s)], which have greatly inconvenienced me. As a loyal customer, this experience has tarnished my perception of your brand, and I am disappointed by the lack of resolution thus far.
    # I urgently request your immediate attention to rectify this situation. My expectations include [mention any specific actions or resolutions you expect from the customer service team].
    # Please prioritize this matter and provide me with a prompt response to ensure my confidence in your company's commitment to customer satisfaction.
    # I trust that you will take swift action to address my concerns and restore my faith in your brand.
    # Thank you for your attention to this urgent matter.
    # """

    for new_email_msg in new_email_msg_array:
    
        criticality_script = f"""use this criticality categorization {ciricality_categorization}
        and tell me the criticality of this email body {new_email_msg["body"]}
        no need of explanations only provide me the criticality category. don't output any other word"""



        # Send the email body to Gemini for criticality identification
        response = llm.invoke(criticality_script)

        # Print the analysis (replace with sentiment score when available)
        print(f"criticality category: {response.content}")
        
        # update the criticality_category
        new_email_msg["criticality_category"]=response.content





