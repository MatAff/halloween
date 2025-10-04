import datetime
import time
import threading

import RPi.GPIO as GPIO 

TRIGGER_DURATION_1 = 5.0
BUTTON_PIN = 16

# Clean up from any previous crashes
GPIO.cleanup() 

trigger_1 = False
trigger_time_1 = datetime.datetime.min 
running = True


def time_since(timestamp):
    delta = datetime.datetime.now() - timestamp
    return delta.total_seconds()


def run_sequence(duration):
    """Sequence logic runs for 'duration' seconds and automatically manages the flag."""
    global trigger_1
    
    print(f"\n[THREAD] Sequence started! Running for {duration} seconds.")
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # --- YOUR SEQUENCE CODE GOES HERE REPEATEDLY ---
        remaining = duration - (time.time() - start_time)
        print(f'\r[THREAD] Sequence active... {remaining:.1f}s remaining.', end='', flush=True) 
        time.sleep(0.1) # Delay to prevent 100% CPU usage inside the thread
        
    print("\n[THREAD] Sequence finished.")
    
    trigger_1 = False 


def trigger_1_callback(channel):
    global trigger_1
    global trigger_time_1
    
    if not trigger_1:
        trigger_1 = True
        trigger_time_1 = datetime.datetime.now()
        print("\n[EVENT] Button pressed! Starting sequence thread...")
        
        # Start the sequence on a new thread
        sequence_thread = threading.Thread(target=run_sequence, args=(TRIGGER_DURATION_1,))
        sequence_thread.start()


# --- GPIO Setup  ---
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BOARD) 

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=trigger_1_callback, bouncetime=200) 

print(f"System Ready. Listening on Pin {BUTTON_PIN}. Sequence duration: {TRIGGER_DURATION_1}s.")
print("The main loop is non-blocking. Press Ctrl+C to exit.")


try:
    while running:
        main_time = time.strftime('%H:%M:%S', time.localtime())
        status = "BUSY" if trigger_1 else "READY"
        print(f"\r[MAIN LOOP] Time: {main_time} | Status: {status}", end='', flush=True) 
        
        time.sleep(0.05) 

except KeyboardInterrupt:
    print("\nExiting program.")

finally:
    GPIO.cleanup()