import json
import pandas as pd
import plotly.express as px
import numpy as np
from scipy.signal import find_peaks


class EKGdata:

    def __init__(self, ekg_dict):
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(self.data, sep='\t', header=None, names=['Messwerte in mV', 'Zeit in ms'])
        self.peaks = None
        self.hr = None

    @staticmethod
    def load_by_id(test_id):
        with open("data/person_db.json", "r") as file:
            data = json.load(file)

        for person in data:
            for test in person.get("ekg_tests", []):
                if test["id"] == test_id:
                    return EKGdata(test)

        return None

    def find_peaks(self, distance=200, height=0.5):
        signal = self.df['Messwerte in mV']
        peaks, _ = find_peaks(signal, distance=distance, height=height)
        self.peaks = peaks
        return peaks

    def estimate_hr(self):
        if self.peaks is None:
            self.find_peaks()

        times_ms = self.df["Zeit in ms"].iloc[self.peaks].values
        rr_intervals_ms = np.diff(times_ms)
        mean_rr = np.mean(rr_intervals_ms)
        self.hr = 60000 / mean_rr if mean_rr > 0 else 0
        return round(self.hr, 1)

    def plot_time_series(self):
        df = self.df.copy()

        # Zeit bei 0 starten
        start_time = df["Zeit in ms"].iloc[0]
        df["Zeit in ms"] = df["Zeit in ms"] - start_time
        df["Zeit in s"] = df["Zeit in ms"] / 1000

        # Nur 0–10 Sekunden
        df_plot = df[df["Zeit in ms"] <= 10000]

        fig = px.line(df_plot, x="Zeit in s", y="Messwerte in mV", title="EKG Zeitreihe (0–10 s)")

        # Peaks markieren (wenn vorhanden und im Bereich)
        if self.peaks is not None:
            peak_times_ms = self.df["Zeit in ms"].iloc[self.peaks].values - start_time
            peaks_in_range = self.peaks[peak_times_ms <= 10000]

            df_peaks = df.iloc[peaks_in_range]
            df_peaks["Zeit in s"] = df_peaks["Zeit in ms"] / 1000

            fig.add_scatter(
                x=df_peaks["Zeit in s"],
                y=df_peaks["Messwerte in mV"],
                mode='markers',
                marker=dict(color='red', size=6),
                name="Peaks"
            )

        fig.update_layout(xaxis_title="Zeit (s)", yaxis_title="Messwerte in mV")
        return fig




if __name__ == "__main__":
    ekg = EKGdata.load_by_id(1)
    if ekg:
        ekg.find_peaks()
        hr = ekg.estimate_hr()
        print(f"Herzfrequenz: {hr} bpm")
        fig = ekg.plot_time_series()
        fig.show()
    else:
        print("EKG-Test mit dieser ID nicht gefunden.")
