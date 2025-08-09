# code/logger.py
# This module handles logging of focus states and blink rates to a CSV file.
import csv 
from datetime import datetime, timedelta

class Logger: 
    def __init__(self, filename="focus_log.csv"):
        self.filename = filename
        self.last_logged_time = None
        try:
            with open(self.filename, 'x', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["timestamp", "blink_rate", "focus_score" "focus_status"])
        except FileExistsError:
            pass

    def log(self, blink_rate, focus_score, focus_status):
        now = datetime.now()
        if not self.last_logged_time or (now - self.last_logged_time).total_seconds() >= 5:
            with open(self.filename, 'a', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                timestamp = now.isoformat()
                writer.writerow([timestamp, blink_rate, focus_score, focus_status])
            self.last_logged_time = now
