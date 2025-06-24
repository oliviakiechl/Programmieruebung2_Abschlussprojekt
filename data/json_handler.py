import json
import os

def add_person_to_json(firstname, lastname, birth_year, file_path="data/person_db.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    if data:
        new_id = max(person["id"] for person in data) + 1
    else:
        new_id = 1

    new_person = {
        "id": new_id,
        "firstname": firstname,
        "lastname": lastname,
        "date_of_birth": birth_year,
        "picture_path": "",
        "ekg_tests": []
    }

    data.append(new_person)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return new_person
