import subprocess
import pwd
import os



# ... (other imports and setup) ...

# Use the ABSOLUTE path to mpg123 (e.g., /usr/bin/mpg123)
MPG_COMMAND = '/usr/bin/mpg123'
MP3_FILE_PATH = '/home/pi/git/halloween/sounds/zombie.mp3' # <-- Confirming the full working path here

# ... inside run_sequence function ...
try:
    print('Calling sounds with mpg123...')
    
    # Construct the command as a single string

    command_string = f"{MPG_COMMAND} -q -a hw:1,0 {MP3_FILE_PATH}"

    # process = subprocess.Popen(
    #     ['sudo', '-u', 'pi', '/usr/bin/mpg123', '/home/pi/git/halloween/zombie.mp3'], preexec_fn=demote(user_uid, user_gid), env=env
    # )

    subprocess.Popen(command_string,
                      shell=True, # <--- CRITICAL CHANGE: Use the shell
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)
    
except FileNotFoundError:
    print(f"\n[AUDIO ERROR] mpg123 executable not found at {MPG_COMMAND}.")
