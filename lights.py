import datetime
import time
import threading
from gpiozero import Button
import board
import subprocess
import serial
import vlc

import pygame

ARDUINO_PORT_0 = '/dev/ttyUSB0'
BAUD_RATE = 9600

arduino = None

arduino = serial.Serial(ARDUINO_PORT_0, BAUD_RATE, timeout=1) 
print(f"Serial connection established on {ARDUINO_PORT_0}.")
time.sleep(2)

try:
    while True:
        print("[SERIAL] Sent 'A' command to Arduino.")
        arduino.write('A'.encode('ascii')) 
        time.sleep(10)
except Exception as e:
    ...