# eeg_reader.py - simplified for MVP
import pandas as pd
import time
import os

class EEGReader:
    def __init__(self, path, poll_interval=1.0):
        self.path = os.path.abspath(path)
        self.poll_interval = poll_interval
        self._last_index = -1  # keeps track of last row read

    def get_latest_attention(self):
        """Return the latest attention value from EEG file if updated, else None."""
        if not os.path.exists(self.path):
            return None
        try:
            df = pd.read_csv(self.path, engine="python")
            if df.empty:
                return None

            # Only process new row
            latest_index = df.index[-1]
            if latest_index == self._last_index:
                return None  # no new row yet
            self._last_index = latest_index

            row = df.iloc[-1]

            # Try 'attention' column first
            attention = row.get("attention", None)
            if pd.isna(attention):
                # fallback: compute from bands
                low_beta = row.get("low_beta", 0.0)
                high_beta = row.get("high_beta", 0.0)
                low_alpha = row.get("low_alpha", 0.0)
                high_alpha = row.get("high_alpha", 0.0)
                ratio = (low_beta + high_beta) / max(low_alpha + high_alpha, 1e-6)
                # map ratio 0->5 to 0->100
                attention = min(100, max(0, (ratio/5.0)*100))
            return float(attention)
        except Exception as e:
            print("EEG read error:", e)
            return None

    def run_poll(self):
        """Generator that yields new attention values as they come."""
        while True:
            val = self.get_latest_attention()
            yield val
            time.sleep(self.poll_interval)


# Quick test/demo
if __name__ == "__main__":
    reader = EEGReader("C:\\Users\\prahm\\OneDrive\\Desktop\\MatrixInfo.csv", poll_interval=1.0)
    print("Polling EEG file...")
    for val in reader.run_poll():
        if val is not None:
            print("New attention:", val)
