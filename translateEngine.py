import torch 
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer 
from IndicTransToolkit import IndicProcessor # NEW 
import re
import json

# ---------------------------- # CONFIG # ---------------------------- 
MODEL_NAME = "law-ai/InLegalTrans-En2Indic-1B"
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
TOKENIZER_MODEL = "ai4bharat/indictrans2-en-indic-1B"

# ---------------------------- # LOAD MODEL + TOKENIZER # ---------------------------- 

model = None
tokenizer = None


def load_translation_model():

    global model, tokenizer

    if model is None:

        print("Loading translation model...")

        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL, trust_remote_code=True)

        model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME, trust_remote_code=True, attn_implementation="eager", low_cpu_mem_usage=True
        ).to(DEVICE)
        
    model.eval()
    print("Model loaded successfully!")


def unload_translation_model():

    global model, tokenizer

    del model
    del tokenizer

    model = None
    tokenizer = None

    import gc
    import torch

    gc.collect()
    torch.cuda.empty_cache()

# Load legal dictionary
with open("legal_terms.json", "r", encoding="utf-8") as f:
    LEGAL_TERMS = json.load(f)

def protect_case_numbers(text):

    replacements = {}

    patterns = [
        r'\b[A-Z]{1,10}\(?[A-Z]*\)?[-./ ]?\d+/?\d*\b'
    ]

    count = 0

    for pattern in patterns:

        matches = re.finditer(pattern, text)

        for match in matches:

            original = match.group(0)

            token = f"CASEREF{count}XYZ"

            replacements[token] = original

            text = text.replace(original, token)

            count += 1

    return text, replacements


def protect_legal_terms(text):

    replacements = {}

    for i, (eng, mal) in enumerate(LEGAL_TERMS.items()):

        # Strong placeholder token
        token = f"ZXQ{i}KPX"

        pattern = re.compile(rf"\b{re.escape(eng)}\b", re.IGNORECASE)

        if pattern.search(text):

            replacements[token] = mal

            text = pattern.sub(token, text)

    return text, replacements


def restore_legal_terms(text, replacements):

    # Convert list to string if needed
    if isinstance(text, list):
        text = " ".join([str(t) for t in text])

    text = str(text)

    # Restore placeholders
    for token, mal in replacements.items():

        # Handle token variations with spaces
        spaced_token = " ".join(list(token))

        text = text.replace(token, mal)
        text = text.replace(spaced_token, mal)

    # Clean extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# ---------------------------- # LANGUAGE CODE MAP # ---------------------------- 
LANG_MAP = { "english": "eng_Latn", "malayalam": "mal_Mlym", "hindi": "hin_Deva", "tamil": "tam_Taml" } 

def clean_translation(text): 
    # remove language tags like eng_Latn, mal_Mlym etc. 
    text = re.sub(r'\b[a-z]{3}_[A-Za-z]{4}\b', '', text) # remove extra spaces 
    text = re.sub(r'\s+', ' ', text).strip() 
    return text 

# ---------------------------- # TRANSLATION FUNCTION # ---------------------------- 
def translate(text, src_lang="english", tgt_lang="malayalam"): 
    ip = IndicProcessor(inference=True) 
    src_code = LANG_MAP[src_lang] 
    tgt_code = LANG_MAP[tgt_lang] # ✅ Preprocess only (no manual tags) 

    protected_text, replacements = protect_legal_terms(text)
    protected_text, case_replacements = protect_case_numbers(protected_text)
    replacements.update(case_replacements)

    batch = ip.preprocess_batch([protected_text], src_lang=src_code, tgt_lang=tgt_code) 
    inputs = tokenizer(batch, max_length=256, return_tensors="pt", padding=True, truncation=True, return_attention_mask=True, ).to(DEVICE) 
    
    with torch.no_grad(): 
        generated_tokens = model.generate( **inputs, max_length=256, num_beams=5, do_sample=False, early_stopping=True, ) 
        decoded = tokenizer.batch_decode( generated_tokens.detach().cpu(), skip_special_tokens=True ) 
        translations = ip.postprocess_batch(decoded, lang=tgt_code)
        translated_text = translations[0]

        translated_text = restore_legal_terms(translated_text, replacements)

        return clean_translation(translated_text)

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