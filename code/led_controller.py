import pandas as pd
import serial
import time

ARDUINO_PORT = "COM6"
BAUD_RATE = 9600

arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE)
time.sleep(2)

while True:
    df = pd.read_csv("focus_log.csv")
    if not df.empty:
        score = int(df["final_score"].iloc[-1])
        print(f"Sending score: {score}")
        arduino.write(f"{score}\n".encode())
    time.sleep(2)  # check every 2 seconds
