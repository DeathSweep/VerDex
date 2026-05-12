import json
import os

DICT_FILE = "user_dictionary.json"


# ---------------------------------------------------
# Create dictionary file if not exists
# ---------------------------------------------------
if not os.path.exists(DICT_FILE):
    with open(DICT_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


# ---------------------------------------------------
# Load dictionary
# ---------------------------------------------------
def load_dictionary():

    with open(DICT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


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
def add_word():

    dictionary = load_dictionary()

    source = input("Enter original word: ").strip()
    translation = input("Enter translation: ").strip()

    if source in dictionary:
        print("Word already exists.")
        return

    dictionary[source] = translation

    save_dictionary(dictionary)

    print("Word added successfully.")


# ---------------------------------------------------
# Delete word
# ---------------------------------------------------
def delete_word():

    dictionary = load_dictionary()

    source = input("Enter word to delete: ").strip()

    if source not in dictionary:
        print("Word not found.")
        return

    del dictionary[source]

    save_dictionary(dictionary)

    print("Word deleted successfully.")


# ---------------------------------------------------
# Modify word
# ---------------------------------------------------
def modify_word():

    dictionary = load_dictionary()

    source = input("Enter word to modify: ").strip()

    if source not in dictionary:
        print("Word not found.")
        return

    print(f"Current translation: {dictionary[source]}")

    new_translation = input(
        "Enter new translation: "
    ).strip()

    dictionary[source] = new_translation

    save_dictionary(dictionary)

    print("Word modified successfully.")


# ---------------------------------------------------
# Search word
# ---------------------------------------------------
def search_word():

    dictionary = load_dictionary()

    query = input("Search: ").strip().lower()

    found = False

    for source, translation in dictionary.items():

        if (
            query in source.lower()
            or query in translation.lower()
        ):

            print(f"{source} -> {translation}")

            found = True

    if not found:
        print("No matching words found.")


# ---------------------------------------------------
# View all words
# ---------------------------------------------------
def view_dictionary():

    dictionary = load_dictionary()

    if not dictionary:
        print("Dictionary is empty.")
        return

    print("\n--- Dictionary ---\n")

    for source, translation in dictionary.items():
        print(f"{source} -> {translation}")


# ---------------------------------------------------
# Main menu
# ---------------------------------------------------
def main():

    while True:

        print("\n========== Dictionary Editor ==========")

        print("1. Add Word")
        print("2. Delete Word")
        print("3. Modify Word")
        print("4. Search Word")
        print("5. View Dictionary")
        print("6. Exit")

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            add_word()

        elif choice == "2":
            delete_word()

        elif choice == "3":
            modify_word()

        elif choice == "4":
            search_word()

        elif choice == "5":
            view_dictionary()

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid option.")


# ---------------------------------------------------
# Run program
# ---------------------------------------------------
if __name__ == "__main__":
    main()