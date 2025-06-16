import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy.signal import find_peaks


def handle_upload():
    st.header("Eigene EKG-Datei hochladen und analysieren")

    st.markdown("""
    **Erwartetes Format der Datei:**
    - Tab-getrennt (`.txt` oder `.csv`)
    - Zwei Spalten: **Messwerte in mV**, **Zeit in ms**
    - Kein Header notwendig
    """)

    uploaded_file = st.file_uploader("EKG-Datei auswählen", type=["txt", "csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep="\t", header=None, names=["Messwerte in mV", "Zeit in ms"])

            if df.empty or len(df.columns) < 2:
                st.error("Die Datei enthält nicht genügend Daten.")
                return

            st.success("Datei erfolgreich geladen!")
            analyze_ekg_dataframe(df)

        except Exception as e:
            st.error(f"Fehler beim Verarbeiten der Datei: {str(e)}")


def analyze_ekg_dataframe(df):
    # Signal normalisieren (falls nötig)
    df = df.copy()
    df["Zeit in ms"] = df["Zeit in ms"] - df["Zeit in ms"].iloc[0]
    df["Zeit in s"] = df["Zeit in ms"] / 1000

    # Peaks berechnen
    signal = df["Messwerte in mV"]
    peaks, _ = find_peaks(signal, distance=200, height=0.5)

    if len(peaks) < 2:
        st.warning("Nicht genug Herzschläge erkannt für Analyse.")
        return

    # Herzfrequenz berechnen
    times_ms = df["Zeit in ms"].iloc[peaks].values
    rr_intervals_ms = np.diff(times_ms)
    hr_values = 60000 / rr_intervals_ms
    avg_hr = round(np.mean(hr_values), 1)
    min_hr = int(np.min(hr_values))
    max_hr = int(np.max(hr_values))
    duration_min = round(df["Zeit in ms"].iloc[-1] / 60000, 2)

    # Ergebnisse anzeigen
    st.write(f"**Durchschnittliche Herzfrequenz:** {avg_hr} bpm")
    st.write(f"**Minimale Herzfrequenz:** {min_hr} bpm")
    st.write(f"**Maximale Herzfrequenz:** {max_hr} bpm")
    st.write(f"**Dauer der Aufnahme:** {duration_min} Minuten")

    # Plot
    df_plot = df[df["Zeit in ms"] <= 10000]  # nur erste 10 Sekunden
    fig = px.line(df_plot, x="Zeit in s", y="Messwerte in mV", title="EKG Zeitreihe (0–10 s)")

    peaks_in_range = peaks[df["Zeit in ms"].iloc[peaks] <= 10000]
    df_peaks = df.iloc[peaks_in_range].copy()
    df_peaks["Zeit in s"] = df_peaks["Zeit in ms"] / 1000

    fig.add_scatter(
        x=df_peaks["Zeit in s"],
        y=df_peaks["Messwerte in mV"],
        mode='markers',
        marker=dict(color='red', size=6),
        name="Peaks"
    )

    fig.update_layout(xaxis_title="Zeit (s)", yaxis_title="Messwerte in mV")
    st.plotly_chart(fig, use_container_width=True)