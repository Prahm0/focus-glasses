# logger.py
import csv
from datetime import datetime

class Logger:
    def __init__(self, filename="focus_log.csv"):
        self.filename = filename
        self.last_logged_time = None
        try:
            with open(self.filename, 'x', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["timestamp", "focus_score", "eeg_score", "final_score", "focus_status"])
        except FileExistsError:
            pass

    def log(self, focus_score, eeg_score, final_score, focus_status):
        # Replace None EEG values with 0
        if eeg_score is None:
            eeg_score = 0
        now = datetime.now()
        if not self.last_logged_time or (now - self.last_logged_time).total_seconds() >= 5:
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([now.isoformat(), focus_score, eeg_score, final_score, focus_status])
            self.last_logged_time = now
