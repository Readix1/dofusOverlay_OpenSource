import pyautogui as pa
import time
from keyboard import press, write

def invite_all(name_list, ):
    # pa.click(100, 100)  # Click to focus the application window
    time.sleep(0.05)
    # pa.hotkey('enter')
    press('enter')

    for name in name_list:
        time.sleep(0.07)
        write("/invite "+name)
        time.sleep(0.07)
        pa.press('enter')





if __name__ == "__main__":
    invite_all(["sang-time", "muul"])