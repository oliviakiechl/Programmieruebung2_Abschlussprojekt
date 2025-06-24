import streamlit as st
import pandas as pd
from PIL import Image
from login import login
from person import Person
from ekgdata import EKGdata
from upload import handle_upload
from herzrate import interactive_hr_plot
from pdf_export import export_pdf

# Seitenlayout konfigurieren
st.set_page_config(page_title="EKG Analyse", layout="wide")

# --- Login ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
    st.stop()

# Titel
st.title("EKG APP")

# Sidebar Navigation
seiten = ["Personendaten", "EKG-Auswertung", "Herzfrequenz-Verlauf", "Eigene EKG-Datei hochladen", "PDF-Bericht erstellen"]
if st.session_state["role"] == "arzt":
    seiten.append("Neue Person anlegen")
seite = st.sidebar.radio("Navigation", seiten)
# Session-State initialisieren
if 'current_user_name' not in st.session_state:
    st.session_state.current_user_name = 'None'
if 'current_person' not in st.session_state:
    st.session_state.current_person = None

# Daten laden
person_data_list = Person.load_person_data()
person_names = Person.get_person_list(person_data_list)


# --- Seite: Personendaten ---
if seite == "Personendaten":
    st.header("Versuchsperson auswählen")

    selected_name = st.selectbox(
        "Versuchsperson",
        options=person_names,
        index=person_names.index(st.session_state.current_user_name)
        if st.session_state.current_user_name in person_names else 0,
        key="sbVersuchsperson"
    )

    if selected_name != st.session_state.current_user_name:
        st.session_state.current_user_name = selected_name
        person_dict = Person.find_person_data_by_name(selected_name)
        if person_dict:
            st.session_state.current_person = Person(person_dict)
        else:
            st.session_state.current_person = None

    if st.session_state.current_person is not None:
        person = st.session_state.current_person
        st.write(f"ID: {person.id}")

        image = Image.open(person.picture_path)
        st.image(image, caption=st.session_state.current_user_name)

        st.write(f"Name: {st.session_state.current_user_name}")
        st.write(f"Geburtsjahr: {person.date_of_birth}")
        st.write(f"Alter der Person: {person.calculate_age()} Jahre")

        # --- Nur für Ärzt:innen sichtbar: Bearbeitungsbereich ---
        if st.session_state["role"] == "arzt":
            st.subheader("Personendaten bearbeiten")

            new_firstname = st.text_input("Vorname", value=person.firstname)
            new_lastname = st.text_input("Nachname", value=person.lastname)
            new_dob = st.text_input("Geburtsjahr", value=str(person.date_of_birth))
            new_picture = st.file_uploader("Neues Bild hochladen (optional)", type=["jpg", "png", "jpeg"])

            if st.button("Änderungen speichern"):
                import json
                import os

                with open("data/person_db.json", "r", encoding="utf-8") as f:
                    all_persons = json.load(f)

                for p in all_persons:
                    if p["id"] == person.id:
                        p["firstname"] = new_firstname
                        p["lastname"] = new_lastname
                        p["date_of_birth"] = int(new_dob)

                        if new_picture is not None:
                            image_path = f"data/pictures/{person.id}.png"
                            with open(image_path, "wb") as img_file:
                                img_file.write(new_picture.getbuffer())
                            p["picture_path"] = image_path

                        break

                with open("data/person_db.json", "w", encoding="utf-8") as f:
                    json.dump(all_persons, f, indent=4, ensure_ascii=False)

                st.success("Daten wurden erfolgreich aktualisiert. Bitte Seite neu laden.")
        else:
            st.info("Nur Ärzt:innen können Personendaten bearbeiten.")
    else:
        st.warning("Die gewählte Person konnte nicht gefunden werden.")


# --- Seite: EKG-Auswertung ---
elif seite == "EKG-Auswertung":
    st.header("EKG-Daten analysieren")

    if st.session_state.current_person is not None:
        person = st.session_state.current_person
        ekg_tests = person.ekg_tests

        if ekg_tests:
            ekg_ids = [test["id"] for test in ekg_tests]
            selected_ekg_id = st.selectbox("Wähle EKG-Test-ID", ekg_ids)

            selected_test = next((t for t in ekg_tests if t["id"] == selected_ekg_id), None)

            if selected_test:
                ekg = EKGdata(selected_test)
                ekg.find_peaks()
                hr = ekg.estimate_hr()

                anomalies = ekg.check_for_anomalies()
                if anomalies:
                    st.subheader("Auffälligkeiten im EKG") 
                    for a in anomalies:
                       st.error(a)
                else:
                    st.success("Keine Auffälligkeiten erkannt.")

                st.write(f"Datum des Tests: {ekg.date}")
                st.write(f"Berechnete Herzfrequenz: {hr} bpm")
                st.write(f"Minimale Herzfrequenz: {ekg.get_min_hr()} bpm")
                st.write(f"Maximale Herzfrequenz: {ekg.get_max_hr()} bpm")
                st.write(f"Dauer der Aufnahme: {ekg.get_signal_duration_min()} Minuten")

                # Kommentar anzeigen (wenn vorhanden)
                current_comment = selected_test.get("comment", "")
                st.subheader("Ärztliche Notiz zum Test")

                if st.session_state["role"] == "arzt":
                    updated_comment = st.text_area("Notiz eingeben / bearbeiten", value=current_comment)
                    if st.button("Notiz speichern"):
                        import json

                        with open("data/person_db.json", "r", encoding="utf-8") as f:
                            all_persons = json.load(f)

                        # Finde passende Person und Test
                        for person in all_persons:   
                            for test in person.get("ekg_tests", []):
                                if test["id"] == selected_test["id"]:
                                    test["comment"] = updated_comment
                                    break

                        with open("data/person_db.json", "w", encoding="utf-8") as f:
                            json.dump(all_persons, f, indent=4, ensure_ascii=False)
                        st.success("Notiz wurde erfolgreich gespeichert.")

                else:
                    if current_comment:
                        st.info(f"Kommentar von Ärzt:in: _{current_comment}_")
                    else: 
                        st.info("Keine Notiz vorhanden.")  
    

                # Zeit-Slider zur Auswahl des Darstellungsbereichs
                max_seconds = ekg.df["Zeit in ms"].max() / 1000
                time_range = st.slider(
                    "Zeitausschnitt für EKG-Anzeige (in Sekunden)",
                    min_value=0.0,
                    max_value=float(max_seconds),
                    value=(0.0, min(10.0, max_seconds)),
                    step=1.0
                )

                fig = ekg.plot_time_series(time_range=time_range)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Der ausgewählte EKG-Test konnte nicht geladen werden.")
        else:
            st.info("Für diese Person sind keine EKG-Tests vorhanden.")
    else:
        st.info("Bitte zuerst eine Person auf der Seite 'Personendaten' auswählen.")

# --- Seite: Herzfrequenz-Verlauf ---
elif seite == "Herzfrequenz-Verlauf":
    st.header("Herzfrequenz über Zeit")

    if st.session_state.current_person is not None:
        person = st.session_state.current_person
        ekg_tests = person.ekg_tests

        if ekg_tests:
            ekg_ids = [test["id"] for test in ekg_tests]
            selected_ekg_id = st.selectbox("Wähle EKG-Test-ID", ekg_ids, key="herzrate_ekg_select")

            selected_test = next((t for t in ekg_tests if t["id"] == selected_ekg_id), None)

            if selected_test:
                ekg = EKGdata(selected_test)
                ekg.find_peaks()

                interactive_hr_plot(ekg.df)
            else:
                st.warning("Der EKG-Test konnte nicht geladen werden.")
        else:
            st.warning("Für diese Person sind keine EKG-Daten vorhanden.")
    else:
        st.info("Bitte zuerst eine Person auswählen.")

# --- Seite: Eigene EKG-Daten hochladen ---
elif seite == "Eigene EKG-Datei hochladen":
    st.header("Eigene EKG-Daten hochladen")

    uploaded_file = st.file_uploader("Lade eine EKG-Datei im TXT-Format hoch", type=["txt"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep="\t", header=None, names=["Messwerte in mV", "Zeit in ms"])
            st.success("Datei erfolgreich geladen!")

            st.subheader("Vorschau der EKG-Daten")
            st.write(df.head())

            dummy_test = {
                "id": "custom",
                "date": "heute",
                "result_link": uploaded_file
            }
            ekg = EKGdata(dummy_test)
            ekg.df = df
            ekg.find_peaks()

            st.write(f"Berechnete Herzfrequenz: {ekg.estimate_hr()} bpm")
            st.write(f"Minimale Herzfrequenz: {ekg.get_min_hr()} bpm")
            st.write(f"Maximale Herzfrequenz: {ekg.get_max_hr()} bpm")
            st.write(f"Dauer der Aufnahme: {ekg.get_signal_duration_min()} Minuten")

            fig = ekg.plot_time_series()
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Fehler beim Verarbeiten der Datei: {e}")

# --- Seite: Neue Person anlegen (nur für Ärzt:innen) ---
elif seite == "Neue Person anlegen":
    st.header("Neue Person anlegen")

    if st.session_state["role"] != "arzt":
        st.info("Dieser Bereich ist nur für Ärzt:innen zugänglich.")
    else:
        st.subheader("Basisdaten eingeben")
        firstname = st.text_input("Vorname")
        lastname = st.text_input("Nachname")
        birth_year = st.number_input("Geburtsjahr", min_value=1900, max_value=2100, step=1)

        image_file = st.file_uploader("Bild der Person hochladen", type=["jpg", "jpeg", "png"])

        st.subheader("Optional: EKG-Test hinzufügen")
        ekg_file = st.file_uploader("EKG-Datei (TXT)", type=["txt"])
        test_date = st.text_input("Datum des EKG-Tests (z. B. 2025-06-23)")

        if st.button("Person speichern"):
            import json
            import os
            import uuid

            with open("data/person_db.json", "r", encoding="utf-8") as f:
                all_persons = json.load(f)

            new_id = max(p["id"] for p in all_persons) + 1 if all_persons else 1

            picture_path = ""
            if image_file:
                picture_path = f"data/pictures/{new_id}.png"
                with open(picture_path, "wb") as f:
                    f.write(image_file.getbuffer())

            ekg_tests = []
            if ekg_file and test_date:
                ekg_id = max(
                    (test["id"] for p in all_persons for test in p.get("ekg_tests", [])),
                    default=0
                ) + 1
                ekg_path = f"data/ekg_data/{uuid.uuid4().hex[:8]}_{ekg_file.name}"
                with open(ekg_path, "wb") as f:
                    f.write(ekg_file.getbuffer())
                ekg_tests.append({
                    "id": ekg_id,
                    "date": test_date,
                    "result_link": ekg_path
                })

            new_person = {
                "id": new_id,
                "firstname": firstname,
                "lastname": lastname,
                "date_of_birth": int(birth_year),
                "picture_path": picture_path,
                "ekg_tests": ekg_tests
            }

            all_persons.append(new_person)

            with open("data/person_db.json", "w", encoding="utf-8") as f:
                json.dump(all_persons, f, indent=4, ensure_ascii=False)

            st.success("Person erfolgreich angelegt!")


# --- Seite: PDF-Bericht erstellen (nur für Ärzt:innen) ---
elif seite == "PDF-Bericht erstellen":
    st.header("PDF-Bericht eines EKG-Tests erstellen")

    if st.session_state["role"] != "arzt":
        st.info("Nur Ärzt:innen können PDF-Berichte erstellen.")
    elif st.session_state.current_person is None:
        st.info("Bitte zuerst eine Person auf der Seite 'Personendaten' auswählen.")
    else:
        from pdf_export import export_pdf
        person = st.session_state.current_person
        ekg_tests = person.ekg_tests

        if not ekg_tests:
            st.warning("Diese Person hat keine EKG-Tests.")
        else:
            test_ids = [t["id"] for t in ekg_tests]
            selected_id = st.selectbox("Wähle EKG-Test für PDF-Bericht", test_ids)
            selected_test = next(t for t in ekg_tests if t["id"] == selected_id)

            from ekgdata import EKGdata
            ekg = EKGdata(selected_test)
            ekg.find_peaks()

            if st.button("PDF-Bericht generieren"):
                pdf_path = export_pdf(person, selected_test, ekg)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 Bericht herunterladen",
                        data=f,
                        file_name="ekg_bericht.pdf",
                        mime="application/pdf"
                    )
