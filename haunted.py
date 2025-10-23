import os
import random
import datetime
import time
import threading
from gpiozero import Button
import board
import subprocess
import serial
import vlc

import pygame
# import RPi.GPIO as GPIO 


BUTTON_PIN_BCM = 24 # BCM Pin 23, which corresponds to BOARD Pin 16
BUTTON2_PIN_BCM = 23
TRIGGER_DURATION_1 = 1.0

sound_folder = "/home/pi/git/halloween/sounds"
sound_files = [os.path.join(sound_folder, f) for f in os.listdir(sound_folder)]

ambient_sound_folder = "/home/pi/git/halloween/ambientsounds"
ambient_sound_files = [os.path.join(ambient_sound_folder, f) for f in os.listdir(ambient_sound_folder)]
next_ambient_time = 0
next_ambient_random = lambda: time.time() + random.randint(30, 60)

# GPIO.cleanup() 

MPG_COMMAND = '/usr/bin/mpg123'

# Pygame for sound
#pygame.init()
#pygame.mixer.pre_init(44100, -16, 2, 2048) # Setup for 44.1kHz, 16-bit, stereo, 2048 buffer
#my_sound = pygame.mixer.Sound(MP3_FILE_PATH)
#my_sound.set_volume(1.0)

# ARDUINO_PORT = '/dev/ttyACM0'
ARDUINO_PORT_0 = '/dev/ttyUSB0'
ARDUINO_PORT_1 = '/dev/ttyUSB1' 
BAUD_RATE = 9600
arduino = None

trigger_1 = False
trigger_time_1 = datetime.datetime.min
running = True

try:
    arduino = serial.Serial(ARDUINO_PORT_0, BAUD_RATE, timeout=1) 
    print(f"Serial connection established on {ARDUINO_PORT_0}.")
    time.sleep(2)
except serial.SerialException as e:
    print(f"ERROR: Could not connect to Arduino on {ARDUINO_PORT_0}. {e}")
    try:
        arduino = serial.Serial(ARDUINO_PORT_1, BAUD_RATE, timeout=1) 
        print(f"Serial connection established on {ARDUINO_PORT_1}.")
        time.sleep(2)
    except serial.SerialException as e:
        print(f"ERROR: Could not connect to Arduino on {ARDUINO_PORT_1}. {e}")


def time_since(timestamp):
    delta = datetime.datetime.now() - timestamp
    return delta.total_seconds()

def play_sound(MP3_FILE_PATH):
    print(f'Calling sound {MP3_FILE_PATH}')

    # MP3_FILE_PATH = '/home/pi/git/halloween/zombie2.mp3'
    # vlc_instance = vlc.Instance('--aout=alsa', '--no-video') 
    # p = vlc_instance.media_player_new(f"file://{MP3_FILE_PATH}")
    # p.play()

    # Pygame sound
    # my_sound.play()

    command_string = f"{MPG_COMMAND} -q -a hw:1,0 {MP3_FILE_PATH}"
    subprocess.Popen(command_string,
        shell=True, # <--- CRITICAL CHANGE: Use the shell
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)


def run_sequence(duration):
    """Sequence logic runs for 'duration' seconds and automatically manages the flag."""
    global trigger_1
    
    print(f"\n[THREAD] Sequence started! Running for {duration} seconds.")
    start_time = time.time()

    # Play sound
    try:
        play_sound(random.choice(sound_files))

    except FileNotFoundError:
        print(f"\n[AUDIO ERROR] mpg123 executable not found at {MPG_COMMAND}.")

    # Trigger LEDs
    if arduino:
        try:
            arduino.write('A'.encode('ascii')) 
            print("[SERIAL] Sent 'A' command to Arduino.")
        except Exception as e:
            print(f"[SERIAL ERROR] Failed to send command: {e}")

    # update event loop
    while time.time() - start_time < duration:
        remaining = duration - (time.time() - start_time)
        print(f'\r[THREAD] Sequence active... {remaining:.1f}s remaining.', end='', flush=True) 
        time.sleep(0.1)
        
    print("\n[THREAD] Sequence finished.")
    
    trigger_1 = False 


def trigger_1_callback():
    global trigger_1
    global trigger_time_1
    
    # GPIO Zero handles debouncing internally (default is 10ms)
    if not trigger_1:
        trigger_1 = True
        trigger_time_1 = datetime.datetime.now()
        print("\n[EVENT] Button pressed! Starting sequence thread...")
        
        # Start the sequence on a new thread
        sequence_thread = threading.Thread(target=run_sequence, args=(TRIGGER_DURATION_1,))
        sequence_thread.start()


# # --- GPIO Setup  ---
# GPIO.setwarnings(False) 
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(BUTTON_PIN_BCM, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.add_event_detect(BUTTON_PIN_BCM, GPIO.RISING, callback=trigger_1_callback, bouncetime=200) 


# --- GPIO Zero Setup ---
# The Button object defaults to PUD_UP (pull_up=True).
# Since you wired your button for PUD_DOWN (connecting signal to 3.3V), 
# we set pull_up=False to use the internal pull-down resistor.
# Note: No 'bouncetime' needed; it's handled internally.
button = Button(BUTTON_PIN_BCM, pull_up=True, bounce_time=0.2)  # , bounce_time=0.01 
button.when_pressed = trigger_1_callback

print(f"System Ready. Listening on BCM Pin {BUTTON_PIN_BCM} (BOARD Pin 16). Sequence duration: {TRIGGER_DURATION_1}s.")
print("The main loop is non-blocking. Press Ctrl+C to exit.")

try:
    while running:
        main_time = time.strftime('%H:%M:%S', time.localtime())
        status = "BUSY" if trigger_1 else "READY"
        print(f"\r[MAIN LOOP] Time: {main_time} | Status: {status}", end='', flush=True) 

        if time.time() > next_ambient_time:
            next_ambient_time = next_ambient_random()
            play_sound(random.choice(ambient_sound_files))
        
        time.sleep(0.05) 

except KeyboardInterrupt:
    print("\nExiting program.")
