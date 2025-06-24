import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import matplotlib.pyplot as plt

def save_ekg_plot_as_image(ekg_obj, path="temp_plot.png"):
    fig = ekg_obj.plot_time_series()
    fig.write_image(path)
    return path

def export_pdf(person, test, ekg_obj, output_path="ekg_bericht.pdf"):
    # Plot als Bild speichern
    image_path = save_ekg_plot_as_image(ekg_obj)

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

    # Plot-Bild einfügen
    if y > 10 * cm:
        c.drawImage(image_path, x_margin, 2 * cm, width=16 * cm, preserveAspectRatio=True)

    c.showPage()
    c.save()

    # Temporäres Bild löschen
    if os.path.exists(image_path):
        os.remove(image_path)

    return output_path
