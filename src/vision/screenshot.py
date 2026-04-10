import pyautogui
import cv2
import numpy as np

def capture_desktop():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img