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

    def get_min_hr(self):
        # Beispiel: minimale Herzfrequenz anhand minimalen RR Intervalls berechnen
        if self.peaks is None:
            self.find_peaks()
        times_ms = self.df["Zeit in ms"].iloc[self.peaks].values
        rr_intervals_ms = np.diff(times_ms)
        if len(rr_intervals_ms) == 0:
            return 0
        min_rr = np.max(rr_intervals_ms)  # größtes RR Intervall = minimale HR
        min_hr = 60000 / min_rr if min_rr > 0 else 0
        return round(min_hr, 1)

    def get_max_hr(self):
        # Beispiel: maximale Herzfrequenz anhand maximalen RR Intervalls berechnen
        if self.peaks is None:
            self.find_peaks()
        times_ms = self.df["Zeit in ms"].iloc[self.peaks].values
        rr_intervals_ms = np.diff(times_ms)
        if len(rr_intervals_ms) == 0:
            return 0
        max_rr = np.min(rr_intervals_ms)  # kleinstes RR Intervall = maximale HR
        max_hr = 60000 / max_rr if max_rr > 0 else 0
        return round(max_hr, 1)

    def get_signal_duration_min(self):
        start_time = self.df["Zeit in ms"].iloc[0]
        end_time = self.df["Zeit in ms"].iloc[-1]
        duration_min = (end_time - start_time) / 60000  # ms zu Minuten
        return round(duration_min, 2)

    def plot_time_series(self, time_range=None):
        df = self.df.copy()

        start_time = df["Zeit in ms"].iloc[0]
        df["Zeit in ms"] = df["Zeit in ms"] - start_time
        df["Zeit in s"] = df["Zeit in ms"] / 1000

        # Zeitbereich filtern, wenn angegeben
        if time_range is not None:
            start_sec, end_sec = time_range
            df = df[(df["Zeit in s"] >= start_sec) & (df["Zeit in s"] <= end_sec)]
        # Wenn kein Zeitbereich, dann gesamte Daten anzeigen (ohne Filter)

        fig = px.line(df, x="Zeit in s", y="Messwerte in mV", title="EKG Zeitreihe")

        if self.peaks is not None:
            peak_times_sec = (self.df["Zeit in ms"].iloc[self.peaks].values - start_time) / 1000
            if time_range is not None:
                # Peaks nur im angezeigten Bereich markieren
                peaks_in_range_idx = [i for i, t in enumerate(peak_times_sec) if start_sec <= t <= end_sec]
            else:
                peaks_in_range_idx = list(range(len(self.peaks)))

            df_peaks = df.iloc[peaks_in_range_idx]
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

