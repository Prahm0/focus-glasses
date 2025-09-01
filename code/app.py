# For flask and UI
from flask import Flask, render_template, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

LOG_FILE = "focus_log.csv"

def read_log():
    """Read CSV log and return as DataFrame (or empty DF)."""
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        return df
    return pd.DataFrame(columns=["timestamp", "focus_score", "eeg_score", "final_score", "focus_status"])

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/data")
def data():
    df = read_log()
    if df.empty:
        return jsonify({"timestamps": [], "focus_scores": [], "eeg_scores": [], "final_scores": [], "statuses": []})

    return jsonify({
        "timestamps": df["timestamp"].tolist(),
        "focus_scores": df["focus_score"].tolist(),
        "eeg_scores": df["eeg_score"].tolist(),
        "final_scores": df["final_score"].tolist(),
        "statuses": df["focus_status"].tolist(),
    })

if __name__ == "__main__":
    app.run(debug=True)
