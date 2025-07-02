import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime

def export_pdf(person, test, ekg_obj, output_path="ekg_bericht.pdf"):
    # PDF erzeugen
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    x_margin = 2 * cm
    y = height - 2 * cm

    # Titel
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, y, "EKG-Befundbericht")
    y -= 2 * cm

    # Personendaten
    c.setFont("Helvetica", 12)
    c.drawString(x_margin, y, f"Name: {person.firstname} {person.lastname}")
    y -= 1 * cm
    c.drawString(x_margin, y, f"Geburtsjahr: {person.date_of_birth}")
    y -= 1 * cm
    c.drawString(x_margin, y, f"Testdatum: {test['date']}")
    y -= 1 * cm

    # Herzfrequenz-Daten
    hr = ekg_obj.estimate_hr()
    min_hr = ekg_obj.get_min_hr()
    max_hr = ekg_obj.get_max_hr()
    duration = ekg_obj.get_signal_duration_min()

    c.drawString(x_margin, y, f"Herzfrequenz: {hr} bpm (Min: {min_hr}, Max: {max_hr})")
    y -= 1 * cm
    c.drawString(x_margin, y, f"Dauer der Aufnahme: {duration} Minuten")
    y -= 1 * cm

    # Kommentar anzeigen
    comment = test.get("comment", "")
    if comment:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, y, "Ärztliche Notiz:")
        y -= 1 * cm
        c.setFont("Helvetica", 11)
        for line in comment.splitlines():
            c.drawString(x_margin, y, line)
            y -= 0.7 * cm

    # Hinweis statt Plot
    y -= 1 * cm
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(x_margin, y, "Hinweis: Der EKG-Verlauf kann interaktiv in der App analysiert werden.")
    y -= 0.6 * cm
    c.drawString(x_margin, y, "Dieser Bericht enthält eine Zusammenfassung der Herzfrequenz und Auffälligkeiten.")

    c.showPage()
    c.save()

    return output_path
