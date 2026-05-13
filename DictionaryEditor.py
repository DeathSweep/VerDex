import json
import os

DICT_FILE = "base_dictionary.json"


# ---------------------------------------------------
# Create dictionary file if not exists
# ---------------------------------------------------
if not os.path.exists(DICT_FILE):

    with open(DICT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            {},
            f,
            ensure_ascii=False,
            indent=4
        )


# ---------------------------------------------------
# Load dictionary
# ---------------------------------------------------
def load_dictionary():

    try:

        with open(DICT_FILE, "r", encoding="utf-8") as f:

            return json.load(f)

    except Exception:

        return {}


# ---------------------------------------------------
# Save dictionary
# ---------------------------------------------------
def save_dictionary(dictionary):

    with open(DICT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            dictionary,
            f,
            ensure_ascii=False,
            indent=4
        )


# ---------------------------------------------------
# Add word
# ---------------------------------------------------
def add_word(
    source,
    translation,
    word_type="User"
):

    dictionary = load_dictionary()

    source = source.strip()
    translation = translation.strip()

    if not source or not translation:

        return {
            "status": "error",
            "message": "Empty fields"
        }

    # Prevent duplicates
    if source in dictionary:

        return {
            "status": "exists",
            "message": "Word already exists"
        }

    dictionary[source] = {
        "translation": translation,
        "type": word_type
    }

    save_dictionary(dictionary)

    return {
        "status": "success",
        "message": "Word added"
    }


# ---------------------------------------------------
# Delete word
# ---------------------------------------------------
def delete_word(source):

    dictionary = load_dictionary()

    source = source.strip()

    if source not in dictionary:

        return {
            "status": "not_found",
            "message": "Word not found"
        }

    del dictionary[source]

    save_dictionary(dictionary)

    return {
        "status": "success",
        "message": "Word deleted"
    }


# ---------------------------------------------------
# Modify word
# ---------------------------------------------------
def modify_word(
    source,
    new_translation,
    word_type=None
):

    dictionary = load_dictionary()

    source = source.strip()
    new_translation = new_translation.strip()

    if source not in dictionary:

        return {
            "status": "not_found",
            "message": "Word not found"
        }

    dictionary[source]["translation"] = new_translation

    if word_type is not None:

        dictionary[source]["type"] = word_type

    save_dictionary(dictionary)

    return {
        "status": "success",
        "message": "Word modified"
    }


# ---------------------------------------------------
# Search word
# ---------------------------------------------------
def search_word(query):

    dictionary = load_dictionary()

    query = query.strip().lower()

    results = {}

    for source, details in dictionary.items():

        translation = details.get(
            "translation",
            ""
        )

        if (
            query in source.lower()
            or query in translation.lower()
        ):

            results[source] = details

    return results


# ---------------------------------------------------
# View all words
# ---------------------------------------------------
def view_dictionary():

    return load_dictionary()


# ---------------------------------------------------
# Optional terminal test mode
# ---------------------------------------------------
if __name__ == "__main__":

    print(view_dictionary())