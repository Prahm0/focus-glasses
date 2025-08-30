# code/eeg_reader.py
"""
EEGReader - read latest row(s) from an EEG CSV/XLSX file and provide an 'attention' value.
If Attention/Meditation fields are missing or NaN, a fallback attention estimate is computed
from the spectal band columns (beta / alpha ratio).
"""

import pandas as pd
import time
import os
from typing import Optional, Dict

# Tweak these to fit the typical ranges you observe from your device.
# The computed ratio will be mapped to 0..100 by clipping at MAX_RATIO.
_MAX_RATIO_FOR_100 = 5.0  # if ratio >= this -> attention ~100
_EPS = 1e-9

# Known band column name variants (we'll normalize headers to lower_no_space form)
_EXPECTED_BANDS = [
    "Att", "Med",
    "Delta", "Theta",
    "LowAlpha", "HighAlpha",
    "LowBeta", "HighBeta",
    "LowGamma", "MiddleGamma"
]

def _normalize_col_name(s: str) -> str:
    return s.strip().lower().replace(" ", "_").replace("-", "_")

class EEGReader:
    def __init__(self, path: str, poll_interval: float = 0.5):
        """
        path: path to CSV or Excel file being written by EEG software.
        poll_interval: suggested interval for polling (seconds).
        """
        self.path = os.path.abspath(path)
        self.poll_interval = poll_interval
        self._last_df_len = 0

    def _read_file(self) -> Optional[pd.DataFrame]:
        """
        Robustly read CSV or Excel. If the file is locked or incomplete, return None.
        """
        if not os.path.exists(self.path):
            return None
        try:
            if self.path.lower().endswith(".csv"):
                # try a resilient read; engine python sometimes helps with weird files
                df = pd.read_csv(self.path, engine="python")
            else:
                df = pd.read_excel(self.path)
            if df is None or df.shape[0] == 0:
                return None
            # normalize column names
            df = df.rename(columns={c: _normalize_col_name(c) for c in df.columns})
            return df
        except Exception as e:
            # File might be being written by another process. Return None and let caller retry.
            # (Don't print too much in production.)
            # print("EEGReader read error:", e)
            return None

    def get_latest_row(self) -> Optional[pd.Series]:
        """Return the last row from the file as a pandas Series (normalized column names)."""
        df = self._read_file()
        if df is None or df.shape[0] == 0:
            return None
        return df.iloc[-1]

    def get_available_columns(self) -> Optional[list]:
        df = self._read_file()
        if df is None:
            return None
        return list(df.columns)

    def compute_attention_from_bands(self, row: pd.Series) -> Optional[float]:
        """
        If device attention value is missing, compute a fallback attention estimate (0..100)
        from beta/alpha ratio:
            attention_estimate ~ clamp( (low_beta+high_beta)/(low_alpha+high_alpha) )
        This is a heuristic — you should calibrate after examining actual ranges.
        """
        if row is None:
            return None

        def get_val(k):
            return float(row.get(k, 0.0) or 0.0)

        low_beta = get_val("low_beta")
        high_beta = get_val("high_beta")
        low_alpha = get_val("low_alpha")
        high_alpha = get_val("high_alpha")
        high_gamma = get_val("high_gamma")  # optional use

        beta_sum = low_beta + high_beta
        alpha_sum = low_alpha + high_alpha

        # Avoid division by zero
        ratio = (beta_sum + _EPS) / (alpha_sum + _EPS)

        # Simple mapping: ratio 0 -> attention 0, ratio >= _MAX_RATIO_FOR_100 -> attention 100
        attention = (ratio / _MAX_RATIO_FOR_100) * 100.0
        attention = max(0.0, min(100.0, attention))

        # optionally nudge using gamma if present (small boost)
        if high_gamma and high_gamma > 0:
            attention = attention * 0.8 + max(0, min(100, high_gamma)) * 0.2

        return attention

    def parse_row(self, row: pd.Series) -> Dict:
        """
        Returns a dict:
          {
            "timestamp": float(seconds since epoch) or str,
            "attention": float 0..100 or None,
            "meditation": float or None,
            "bands": { delta:..., theta:..., low_alpha:..., ... }
          }
        """
        if row is None:
            return {"timestamp": None, "attention": None, "meditation": None, "bands": {}}

        # collect bands
        bands = {}
        for k in ["delta","theta","low_alpha","high_alpha","low_beta","high_beta","low_gamma","high_gamma"]:
            bands[k] = float(row.get(k, 0.0) or 0.0)

        # get attention/meditation if present (some files call them 'attention' or 'eSense_attention' etc.)
        attention = None
        meditation = None
        # try direct commonly named columns
        if "attention" in row.index:
            try:
                attention = float(row.get("attention"))
            except Exception:
                attention = None
        if "meditation" in row.index:
            try:
                meditation = float(row.get("meditation"))
            except Exception:
                meditation = None

        # fallback compute from bands if attention missing or NaN
        if (attention is None) or (not (0 <= attention <= 100)):
            attention = self.compute_attention_from_bands(row)

        # timestamp handling: if file has explicit timestamp column try to parse it,
        # otherwise use current time
        ts = row.get("timestamp") if "timestamp" in row.index else None
        if ts is None:
            ts = time.time()
        return {"timestamp": ts, "attention": attention, "meditation": meditation, "bands": bands}

    def get_latest(self) -> Optional[Dict]:
        """Convenience: read latest row and return parsed dict or None."""
        row = self.get_latest_row()
        if row is None:
            return None
        return self.parse_row(row)

    def run_poll(self, sleep_between=0.5):
        """Generator: yields parsed latest dict repeatedly (blocking)."""
        while True:
            d = self.get_latest()
            yield d
            time.sleep(sleep_between)


# Quick example usage (run directly for quick debug):
if __name__ == "__main__":
    # replace with your eeg file path
    path = "../eeg_output/eeg.csv"
    reader = EEGReader("C:\\Users\\prahm\\OneDrive\\Desktop\\MatrixInfo.csv", poll_interval=1.0)
    print("Waiting for EEG file:", reader.path)
    for val in reader.run_poll(1.0):
        if val is not None:
            print("EEG:", val)
        else:
            print("no data yet") 
