from api.email_filtering_and_info_generation.services import getProductsList
from transformers import pipeline


MODEL_TAG = "Isotonic/distilbert_finetuned_ai4privacy_v2"
DEVICE = -1

model = pipeline("token-classification", model=MODEL_TAG, tokenizer=MODEL_TAG, device=DEVICE)

async def mask_email_messages(new_email_msg_array):
    
    products = await getProductsList()
    products_words = []
    
    for product in products:
        split_strings = product.split()
        products_words = products_words + split_strings

    for new_email_msg in new_email_msg_array:
        
       
        
        new_email_msg['body'] = mask_text(new_email_msg['body'], products_words)
        
        

def mask_text(unmasked_text, products_words):
        detected_pii_result = model(unmasked_text, aggregation_strategy="simple")
        # print(*detected_pii_result, sep="\n")
        
        entity_map = create_entity_map(detected_pii_result, unmasked_text, products_words)
        masked_text = replace_entities(unmasked_text, entity_map)
        
        return masked_text
    
    

def create_entity_map(model_output, unmasked_text, products_words):
    entity_map = {}
    for token in model_output:
        start = token["start"]
        end = token["end"]
        entity = unmasked_text[start: end]
        
      
        if token["entity_group"] not in ['USERAGENT','CREDITCARDISSUER', 'STATE', 'URL', 'BUILDINGNUMBER', 'DATE', 'TIME', 'JOBTYPE', 'JOBAREA', 'VEHICLEVRM', 'CURRENCYCODE'] and entity not in products_words:
            entity_map[entity] = token["entity_group"]
        
        print("EnTITY MAP", entity_map)
    return entity_map



def replace_entities(text, entity_map):
    for word in entity_map:
        if word in text:
            text = text.replace(word, f"[{entity_map[word]}]")
    return text


