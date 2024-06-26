from transformers import pipeline


MODEL_TAG = "Isotonic/distilbert_finetuned_ai4privacy_v2"
DEVICE = -1

model = pipeline("token-classification", model=MODEL_TAG, tokenizer=MODEL_TAG, device=DEVICE)

def mask_email_messages(new_email_msg_array):
    

    for new_email_msg in new_email_msg_array:
        
       
        
        new_email_msg['subject'] = mask_text(new_email_msg['subject'])
        new_email_msg['body'] = mask_text(new_email_msg['body'])
        

        # print(masked_text)
        

def mask_text(unmasked_text):
        detected_pii_result = model(unmasked_text, aggregation_strategy="simple")
        # print(*detected_pii_result, sep="\n")
        
        entity_map = create_entity_map(detected_pii_result, unmasked_text)
        masked_text = replace_entities(unmasked_text, entity_map)
        
        return masked_text
    
    

def create_entity_map(model_output, unmasked_text):
    entity_map = {}
    for token in model_output:
        start = token["start"]
        end = token["end"]
        entity = unmasked_text[start: end]
        entity_map[entity] = token["entity_group"]
    return entity_map



def replace_entities(text, entity_map):
    for word in entity_map:
        if word in text:
            text = text.replace(word, f"[{entity_map[word]}]")
    return text


