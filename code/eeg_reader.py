# eeg_reader.py - simplified for MVP
import pandas as pd
import time
import os

class EEGReader:
    def __init__(self, path, poll_interval=1.0):
        self.path = os.path.abspath(path)
        self.poll_interval = poll_interval

    def get_latest_bands(self):
        """Return the latest EEG bands if updated, else None."""
        if not os.path.exists(self.path):
            return None
        try:
            # read CSV, skip first 4 rows (adjust as needed)
            df = pd.read_csv(self.path, header=None, skiprows=4, engine="python", skip_blank_lines=True)

            # Rename numeric columns to expected EEG band names
            # Rename numeric columns to expected EEG band names
            df.columns = ["Attention", "Meditation", "Delta", "Theta", "LowAlpha", "HighAlpha", "LowBeta",
              "HighBeta", "LowGamma", "MiddleGamma"]

            # Keep only relevant columns
            df = df[["Delta", "Theta", "LowAlpha", "HighAlpha",
                     "LowBeta", "HighBeta", "LowGamma", "MiddleGamma"]]

            df = df.dropna(how="all")  # remove fully blank rows
            if df.empty:
                return None

            last_row = df.iloc[-1]      # last non-empty row

            # Extract bands
            # Extract bands and convert to float
            delta        = float(last_row["Delta"])
            theta        = float(last_row["Theta"])
            low_alpha    = float(last_row["LowAlpha"])
            high_alpha   = float(last_row["HighAlpha"])
            low_beta     = float(last_row["LowBeta"])
            high_beta    = float(last_row["HighBeta"])
            low_gamma    = float(last_row["LowGamma"])
            middle_gamma = float(last_row["MiddleGamma"])

            return (delta, theta, low_alpha, high_alpha, low_beta, high_beta, low_gamma, middle_gamma)

        except Exception as e:
            print("EEG read error:", e)
            return None

    def run_poll(self):
        """Generator that yields new EEG band values as they come."""
        while True:
            val = self.get_latest_bands()
            yield val
            time.sleep(self.poll_interval)


# Quick test/demo
if __name__ == "__main__":
    reader = EEGReader("C:\\Users\\prahm\\OneDrive\\Desktop\\MatrixInfo.csv", poll_interval=1.0)
    print("Polling EEG file...")
    for val in reader.run_poll():
        if val is not None:
            print("New EEG bands:", val)
