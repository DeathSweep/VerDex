import torch 
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer 
from IndicTransToolkit import IndicProcessor # NEW 
import re

# ---------------------------- # CONFIG # ---------------------------- 
MODEL_NAME = "ai4bharat/indictrans2-en-indic-1B" 
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# ---------------------------- # LOAD MODEL + TOKENIZER # ---------------------------- 
print("Loading model...") 
tokenizer = AutoTokenizer.from_pretrained( "ai4bharat/indictrans2-en-indic-1B", trust_remote_code=True) 
model = AutoModelForSeq2SeqLM.from_pretrained( MODEL_NAME, trust_remote_code=True, attn_implementation="eager", low_cpu_mem_usage=True, ).to(DEVICE) 
model.eval() 

# ---------------------------- # LOAD INDIC PROCESSOR (NEW) # ---------------------------- 
ip = IndicProcessor(inference=True) 
print("Model loaded successfully!")

# ---------------------------- # LANGUAGE CODE MAP # ---------------------------- 
LANG_MAP = { "english": "eng_Latn", "malayalam": "mal_Mlym", "hindi": "hin_Deva", "tamil": "tam_Taml" } 

def clean_translation(text): 
    # remove language tags like eng_Latn, mal_Mlym etc. 
    text = re.sub(r'\b[a-z]{3}_[A-Za-z]{4}\b', '', text) # remove extra spaces 
    text = re.sub(r'\s+', ' ', text).strip() 
    return text 

# ---------------------------- # TRANSLATION FUNCTION # ---------------------------- 
def translate(text, src_lang="english", tgt_lang="malayalam"): 
    src_code = LANG_MAP[src_lang] 
    tgt_code = LANG_MAP[tgt_lang] # ✅ Preprocess only (no manual tags) 
    batch = ip.preprocess_batch([text], src_lang=src_code, tgt_lang=tgt_code) 
    inputs = tokenizer( batch, max_length=256, return_tensors="pt", padding=True, truncation=True, return_attention_mask=True, ).to(DEVICE) 
    
    with torch.no_grad(): 
        generated_tokens = model.generate( **inputs, max_length=256, num_beams=5, do_sample=False, early_stopping=True, ) 
        decoded = tokenizer.batch_decode( generated_tokens.detach().cpu(), skip_special_tokens=True ) 
        translations = ip.postprocess_batch(decoded, lang=tgt_code) 
        return clean_translation(translations[0]) 
    
# ---------------------------- # INTERACTIVE TEST LOOP # ---------------------------- 
if __name__ == "__main__": 
    print("\n--- Translation Engine Ready ---") 
    print("Type 'exit' to quit\n") 
    while True: 
        text = input("Enter English text: ") 
        if text.lower() == "exit": 
            break 
        
        translated = translate(text) 
        print("Malayalam:", translated) 
        print("-" * 50)