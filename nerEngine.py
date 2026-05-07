from transformers import pipeline

# ✅ Use aggregation (CRITICAL FIX)
ner_pipeline = pipeline(
    "token-classification",
    model="hf-tuner/BERT-Indian-legal-NER",
    aggregation_strategy="simple"
)

def get_entities(text):
    print("Loading NER model...")
    results = ner_pipeline(text)
    print("NER Model loaded.")

    entities = {}

    for item in results:
        label = item['entity_group']   # ✅ changed
        value = item['word']
        score = item['score']

        # ✅ proper confidence filtering
        if score < 0.6:
            continue

        if label not in entities:
            entities[label] = []

        entities[label].append(value)

    # ✅ join multiple values
    for key in entities:
        entities[key] = " ".join(entities[key])

    return entities