import serial
import time

ARDUINO_PORT = "COM6"
BAUD_RATE = 9600

try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE)
    time.sleep(2)
except serial.SerialException:
    arduino = None
    print("Could not open Arduino port. Continuing without hardware.")

def send_focus_score(score):
    if arduino:
        arduino.write(f"{score}\n".encode())
