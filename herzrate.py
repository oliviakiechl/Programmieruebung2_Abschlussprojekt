import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from scipy.signal import find_peaks


def calculate_instant_hr(df, peak_distance=200):
    peaks, _ = find_peaks(df["Messwerte in mV"], distance=peak_distance, height=0.5)
    peak_times = df["Zeit in ms"].iloc[peaks].values

    if len(peak_times) < 2:
        return pd.DataFrame(columns=["Zeit in s", "Herzfrequenz"])

    rr_intervals = np.diff(peak_times)
    hr_values = 60000 / rr_intervals
    times_sec = peak_times[1:] / 1000

    hr_df = pd.DataFrame({"Zeit in s": times_sec, "Herzfrequenz": hr_values})
    hr_df["HR_gemittelt"] = hr_df["Herzfrequenz"].rolling(window=5, min_periods=1).mean()
    return hr_df


def interactive_hr_plot(df):
    hr_df = calculate_instant_hr(df)

    if hr_df.empty:
        st.warning("Nicht genügend Peaks für Herzfrequenzberechnung gefunden.")
        return

    min_time = float(hr_df["Zeit in s"].min())
    max_time = float(hr_df["Zeit in s"].max())

    # Zeit-Slider anzeigen
    time_range = st.slider(
        "Zeitraum für Herzfrequenz anzeigen (in Sekunden)",
        min_value=min_time,
        max_value=max_time,
        value=(min_time, max_time),
        step=1.0
    )

    # Daten filtern
    hr_filtered = hr_df[(hr_df["Zeit in s"] >= time_range[0]) & (hr_df["Zeit in s"] <= time_range[1])]

    # Plot anzeigen
    fig = px.line(
        hr_filtered,
        x="Zeit in s",
        y="HR_gemittelt",
        title="Herzfrequenz-Verlauf (gleitender Durchschnitt)",
        labels={"HR_gemittelt": "Herzfrequenz (bpm)"}
    )
    fig.update_layout(xaxis_title="Zeit (s)", yaxis_title="Herzfrequenz (bpm)")
    st.plotly_chart(fig, use_container_width=True)

