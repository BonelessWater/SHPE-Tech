import os
import time
import pyautogui
import pygetwindow as gw

# -------------------------------
# Optional: Get current mouse coordinates
# -------------------------------
def print_mouse_position():
    print("Move your mouse to the desired position. Press Ctrl+C to exit.")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Current mouse position: ({x}, {y})", end="\r")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nFinished capturing mouse positions.")

print_mouse_position()

# -------------------------------
# Wait for and maximize a window by keyword in its title
# -------------------------------
def wait_and_maximize(window_keyword, timeout=10):
    """
    Waits until a window with the given keyword in its title appears,
    then maximizes it. Returns True if successful, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        windows = gw.getWindowsWithTitle(window_keyword)
        if windows:
            window = windows[0]
            if not window.isMaximized:
                window.maximize()
            return True
        time.sleep(0.2)
    return False

# -------------------------------
# Connect via Bluetooth and then close the Settings window
# -------------------------------
def bluetooth_connect():
    # Open Windows Bluetooth settings via URI
    os.startfile("ms-settings:bluetooth")
    time.sleep(2)  # Give additional time for the window to open

    # Wait for the Settings window and maximize it
    if wait_and_maximize("Settings", timeout=10):
        print("Bluetooth settings maximized.")
    else:
        print("Bluetooth settings window not found.")
    
    # Additional sleep to allow the device list to populate
    time.sleep(2)
    
    # Click on the first device (update these coordinates as needed)
    #first_device_coords = (1980, 435)  # Adjust as necessary
    first_device_coords = (1958, 527)  # Adjust as necessary
    pyautogui.moveTo(first_device_coords[0], first_device_coords[1], duration=0.2)
    pyautogui.click()
    
    # Wait for connection to process before closing
    time.sleep(1)
    
    # Close the Settings window
    pyautogui.hotkey('alt', 'f4')
    time.sleep(1)

# -------------------------------
# Open Spotify, maximize it, and click Play
# -------------------------------
def spotify_play():
    os.startfile("spotify:")
    time.sleep(5)  # Wait for Spotify to load

    if wait_and_maximize("Spotify", timeout=10):
        print("Spotify window maximized.")
    else:
        print("Spotify window not found.")
    
    # Click on the Play button (update these coordinates as needed)
    play_button_coords = (1277, 1309)  # Adjust as necessary
    pyautogui.moveTo(play_button_coords[0], play_button_coords[1], duration=0.2)
    pyautogui.click()

def main():
    bluetooth_connect()
    spotify_play()

if __name__ == "__main__":
    main()
