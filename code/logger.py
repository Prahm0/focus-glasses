import csv 
from datetime import datetime

class Logger: 
    def __init__(self, filename="focus_log.csv"):
        self.filename = filename
        # Write header if file does not exist
        try:
            with open(self.filename, 'x', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["timestamp", "blink_rate", "focus_status"])
        except FileExistsError:
            pass
    def log(self, blink_rate, focus_status):
        with open(self.filename, 'a', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer = csv.writer(csvfile)
            timestamp = datetime.now().isoformat()
            writer.writerow([timestamp, blink_rate, focus_status])