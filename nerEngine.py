import re
import spacy

from transformers import pipeline
from spacy.pipeline import EntityRuler

# =========================================================
# LOAD SPACY
# =========================================================

print("Loading spaCy pipeline...")
nlp = spacy.blank("en")

# =========================================================
# ENTITY RULER
# =========================================================

ruler = nlp.add_pipe("entity_ruler")

patterns = [

    # -----------------------------------------------------
    # LEGAL TERMS
    # -----------------------------------------------------

    {
        "label": "LEGAL_ROLE",
        "pattern": [{"LOWER": {"IN": ["petitioner", "respondent", "accused"]}}]
    },

    {
        "label": "ADVOCATE",
        "pattern": [{"LOWER": {"IN": ["adv", "advocate"]}}]
    },

    # -----------------------------------------------------
    # COURTS
    # -----------------------------------------------------

    {
        "label": "COURT",
        "pattern": "High Court"
    },

    {
        "label": "COURT",
        "pattern": "District Court"
    },

    # -----------------------------------------------------
    # POLICE
    # -----------------------------------------------------

    {
        "label": "POLICE_STATION",
        "pattern": [{"TEXT": {"REGEX": ".*Police.*"}}]
    }
]

ruler.add_patterns(patterns)

print("spaCy EntityRuler loaded.")

# =========================================================
# TRANSFORMER NER
# =========================================================

print("Loading transformer NER model...")

ner_pipeline = pipeline(
    "token-classification",
    model="hf-tuner/BERT-Indian-legal-NER",
    aggregation_strategy="simple"
)

print("Transformer NER loaded.")

# =========================================================
# REGEX PATTERNS
# =========================================================

REGEX_PATTERNS = {

    # -----------------------------------------------------
    # CASE NUMBERS
    # -----------------------------------------------------

    "CASE_NUMBER": r'\b[A-Z./()]+\s?\d+/\d{4}\b',

    # -----------------------------------------------------
    # FIR NUMBERS
    # -----------------------------------------------------

    "FIR_NUMBER": r'FIR\s*No\.?\s*\d+/\d{4}',

    # -----------------------------------------------------
    # CRIME NUMBERS
    # -----------------------------------------------------

    "CRIME_NUMBER": r'Crime\s*No\.?\s*\d+/\d{4}',

    # -----------------------------------------------------
    # SECTIONS
    # -----------------------------------------------------

    "SECTION_OF_LAW": r'Section\s+\d+[A-Z]?\s+(IPC|CrPC|NDPS|IA)',

    # -----------------------------------------------------
    # VEHICLE NUMBERS
    # -----------------------------------------------------

    "VEHICLE_NUMBER": r'\b[A-Z]{2}[-\s]?\d{1,2}[-\s]?[A-Z]{1,2}[-\s]?\d{1,4}\b',

    # -----------------------------------------------------
    # PHONE NUMBERS
    # -----------------------------------------------------

    "PHONE_NUMBER": r'\b[6-9]\d{9}\b',

    # -----------------------------------------------------
    # EMAILS
    # -----------------------------------------------------

    "EMAIL": r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',

    # -----------------------------------------------------
    # PINCODE
    # -----------------------------------------------------

    "PINCODE": r'\b\d{6}\b',

    # -----------------------------------------------------
    # MONEY
    # -----------------------------------------------------

    "MONEY": r'₹\s?\d+(?:,\d+)*(?:\.\d+)?'
}

# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove repeated newlines
    text = re.sub(r'\n+', '\n', text)

    # Fix OCR broken spacing
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    return text.strip()

# =========================================================
# REGEX EXTRACTOR
# =========================================================

def regex_extractor(text):

    entities = []

    for label, pattern in REGEX_PATTERNS.items():

        matches = re.finditer(pattern, text)

        for match in matches:

            entities.append({
                "entity": label,
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 1.0,
                "source": "regex"
            })

    return entities

# =========================================================
# SPACY ENTITY RULER EXTRACTOR
# =========================================================

def spacy_extractor(text):

    doc = nlp(text)

    entities = []

    for ent in doc.ents:

        entities.append({
            "entity": ent.label_,
            "text": ent.text,
            "start": ent.start_char,
            "end": ent.end_char,
            "confidence": 0.95,
            "source": "spacy_ruler"
        })

    return entities

# =========================================================
# TRANSFORMER EXTRACTOR
# =========================================================

def transformer_extractor(text):

    results = ner_pipeline(text)

    entities = []

    for item in results:

        score = float(item["score"])

        if score < 0.60:
            continue

        entities.append({
            "entity": item["entity_group"],
            "text": item["word"],
            "start": item["start"],
            "end": item["end"],
            "confidence": round(score, 4),
            "source": "transformer"
        })

    return entities

# =========================================================
# ENTITY MERGER
# =========================================================

def merge_entities(all_entities):

    merged = []
    seen = set()

    for entity in all_entities:

        key = (
            entity["entity"],
            entity["text"].lower(),
            entity["start"],
            entity["end"]
        )

        if key not in seen:
            seen.add(key)
            merged.append(entity)

    return merged

# =========================================================
# VALIDATION LAYER
# =========================================================

def validate_entities(entities):

    validated = []

    for entity in entities:

        text = entity["text"].strip()

        # Remove useless tiny entities
        if len(text) <= 1:
            continue

        # Remove pure punctuation
        if re.fullmatch(r'[\W_]+', text):
            continue

        validated.append(entity)

    return validated

# =========================================================
# MAIN FUNCTION
# =========================================================

def get_entities(text):

    print("===================================")
    print("STARTING LEGAL NER PIPELINE")
    print("===================================")

    # -----------------------------------------------------
    # STEP 1 - NORMALIZATION
    # -----------------------------------------------------

    print("Normalizing text...")
    text = normalize_text(text)

    # -----------------------------------------------------
    # STEP 2 - REGEX EXTRACTION
    # -----------------------------------------------------

    print("Running regex extractor...")
    regex_entities = regex_extractor(text)

    # -----------------------------------------------------
    # STEP 3 - SPACY ENTITY RULER
    # -----------------------------------------------------

    print("Running spaCy EntityRuler...")
    spacy_entities = spacy_extractor(text)

    # -----------------------------------------------------
    # STEP 4 - TRANSFORMER NER
    # -----------------------------------------------------

    print("Running transformer NER...")
    transformer_entities = transformer_extractor(text)

    # -----------------------------------------------------
    # STEP 5 - MERGE
    # -----------------------------------------------------

    print("Merging entities...")

    all_entities = (
        regex_entities +
        spacy_entities +
        transformer_entities
    )

    merged_entities = merge_entities(all_entities)

    # -----------------------------------------------------
    # STEP 6 - VALIDATION
    # -----------------------------------------------------

    print("Validating entities...")

    validated_entities = validate_entities(merged_entities)

    # -----------------------------------------------------
    # STEP 7 - OUTPUT JSON
    # -----------------------------------------------------

    output = {
        "total_entities": len(validated_entities),
        "entities": validated_entities
    }

    print("NER pipeline complete.")

    return output