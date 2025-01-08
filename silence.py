import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from time import sleep
import os
import psutil

def save_screenshot(screenshot, prefix="death"):
    # Create 'screenshots' directory if it doesn't exist
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = f"screenshots/{prefix}_{timestamp}.png"
    
    # Save the image
    screenshot.save(filename)
    #print(f"Screenshot saved: {filename}")

# Function to mute/unmute audio
def set_volume_mute(mute=True):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1 if mute else 0, None)
    print("Audio muted" if mute else "Audio unmuted")

# Function to monitor the screen for a specific pattern
def detect_death_screen():
    template = cv2.imread('death_screen_template.png', 0)
    process = psutil.Process()
    
    # Define region of interest (ROI)
    x, y = 341, 1440
    roi_width = 200
    roi_height = 200
    roi_x = max(0, x - roi_width//2)
    roi_y = max(0, y - roi_height//2)
    
    try:
        while True:
            sleep(0.5)
            loop_start = time.time()
            
            # Measure CPU usage
            cpu_percent = process.cpu_percent()
            if cpu_percent > 1:  # Adjust threshold as needed
                print(f"CPU Usage: {cpu_percent}%")
            
            # Take screenshot of only the ROI
            screenshot = pyautogui.screenshot(region=(0, 1270, 340, 200))
            
            # Save screenshot immediately
            #save_screenshot(screenshot)
            
            # Process for detection
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > 0.8:
                print("Death screen detected! Muting audio.")
                set_volume_mute(True)
            else:
                set_volume_mute(False)


    except KeyboardInterrupt:
        print("Exiting.")

# Function to capture and save screenshot
def take_screenshot(filename='screenshot.png'):
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")

# Main function
if __name__ == "__main__":
    try:
        print("Monitoring for death screen...")
        detect_death_screen()
    except KeyboardInterrupt:
        print("Exiting.")
