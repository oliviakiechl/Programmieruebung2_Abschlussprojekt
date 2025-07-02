import json
import os

def add_login(username, firstname, role="Patient:in", login_path="data/logindaten.json"):
    """Fügt einen neuen Login in logindaten.json ein (oder aktualisiert ihn)."""
    password = firstname.lower() + "123"

    # Datei laden oder leere Login-Daten vorbereiten
    if os.path.exists(login_path):
        with open(login_path, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = {}

    # Neuen Login hinzufügen
    users[username] = {
        "password": password,
        "role": role
    }

    # Datei speichern
    with open(login_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    return password  # Damit du es dem Arzt/der Ärztin anzeigen kannst


def add_person_to_json(firstname, lastname, birth_year, file_path="data/person_db.json"):
    """Fügt eine neue Patient:in zur person_db.json hinzu und erzeugt Zugangsdaten."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    new_id = max([person["id"] for person in data], default=0) + 1

    username = f"{firstname.lower()}.{lastname.lower()}"
    new_person = {
        "id": new_id,
        "firstname": firstname,
        "lastname": lastname,
        "username": username,
        "date_of_birth": birth_year,
        "picture_path": "",
        "ekg_tests": []
    }

    data.append(new_person)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # Zugangsdaten erzeugen
    password = add_login(username, firstname)

    return new_person, password
