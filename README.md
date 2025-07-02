
# 🫀 EKG Analyse App – Abschlussprojekt

Dieses Projekt ist eine interaktive Streamlit-Webanwendung zur Analyse und Verwaltung von EKG-Daten – entstanden im Rahmen der Programmierübung 2.

## 📌 Funktionen

### 🔐 Login mit Rollen
- Ärzt:in: kann Personen bearbeiten, EKG-Tests hinzufügen, Notizen schreiben und PDF-Berichte erstellen
- Patient:in: sieht ausschließlich die eigenen Daten

### 🧑‍⚕️ Personendaten
- Anzeige von Name, Geburtsjahr, Alter, Bild
- Ärzt:innen können Daten bearbeiten (inkl. Bild aktualisieren)

### 💓 EKG-Auswertung
- Herzfrequenz berechnen (durchschnittlich, min/max)
- Zeitbereich interaktiv einstellbar
- Ärztliche Notiz zu jedem Test (editierbar)
- Automatische Anomalie-Erkennung (z. B. bei extremer Herzrate)

### 📈 Herzfrequenz-Verlauf
- Plot mit gleitendem Durchschnitt über den gesamten Zeitraum

### ⬆️ EKG-Datei hochladen
- Eigene .txt-Dateien können geladen und analysiert werden

### ➕ Neue Person anlegen (nur für Ärzt:innen)
- Bild, Daten und optional ein EKG-Test
- Login-Zugang wird automatisch generiert

### 📄 PDF-Bericht exportieren (nur für Ärzt:innen)
- Erstellt einen Bericht mit Eckdaten, Notiz und Bewertung

## 🗂️ Projektstruktur

```
├── main.py                # Zentrale Streamlit-App
├── login.py               # Login-System mit Rollen
├── person.py              # Personenklasse + JSON-Verwaltung
├── ekgdata.py             # Verarbeitung der EKG-Daten
├── pdf_export.py          # PDF-Bericht-Erstellung
├── json_handler.py        # Personen- und Login-Verwaltung
├── herzrate.py            # Gleitender Herzfrequenzplot
├── data/
│   ├── person_db.json     # Personendatenbank
│   ├── logindaten.json    # Login-Zugänge
│   ├── pictures/          # Bilder der Personen
│   └── ekg_data/          # Rohdaten der EKG-Tests (.txt)
```

## 🚀 Starten der App

```bash
streamlit run main.py
```

## 🔧 Abhängigkeiten (in `requirements.txt`)

- streamlit
- pandas
- numpy
- scipy
- plotly
- reportlab
- matplotlib

## 👩‍💻 Entwickelt mit

- Visual Studio Code
- Streamlit
- Git + GitHub
- PDM (für Paketverwaltung)

## 📥 Installation (optional)

```bash
git clone https://github.com/oliviakiechl/Programmieruebung2_Abschlussprojekt.git
cd Programmieruebung2_Abschlussprojekt
pdm install
streamlit run main.py
```
