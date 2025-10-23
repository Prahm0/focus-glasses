import pandas as pd
import serial
import time
import os

# --- CONFIG ---
ARDUINO_PORT = "COM5"  # set your correct Arduino port
BAUD_RATE = 9600
CSV_FILE = "focus_log.csv"
CHECK_INTERVAL = 2  # seconds

# --- INIT ---
arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE)
time.sleep(3)  # wait for Arduino to reset

print("Python-Arduino connection established.")

# --- MAIN LOOP ---
while True:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty and "final_score" in df.columns:
            score = int(df["final_score"].iloc[-1])
            print(f"Sending score: {score}")
            arduino.write(f"{score}\n".encode())
            arduino.flush()  # ensure it's sent immediately
        else:
            print("CSV empty or 'final_score' column missing.")
    else:
        print(f"{CSV_FILE} not found.")
    
    time.sleep(CHECK_INTERVAL)
