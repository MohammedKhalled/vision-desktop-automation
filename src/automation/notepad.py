import pyautogui
import time
import pygetwindow as gw

def open_notepad_at(x, y):

    print(f"   Opening Notepad at ({x}, {y})...")
    pyautogui.doubleClick(x, y)
    time.sleep(2)
    
    
    windows = gw.getWindowsWithTitle("Notepad")
    if windows:
        print(f"   Notepad opened")
        return True
    else:
        print("   Notepad failed to open")
        return False


def close_notepad():
    
    print("   Closing Notepad...")
    
    try:
       
        notepad_windows = gw.getWindowsWithTitle("Notepad")
        
        if not notepad_windows:
            print("   No Notepad window to close")
            return True
        
        
        for window in notepad_windows:
            try:
                
                window.close()
                print(f"   Closed window: {window.title}")
            except Exception as e:
                print(f"   Could not close {window.title}: {e}")
        
        
        time.sleep(1)
        
        
        remaining = gw.getWindowsWithTitle("Notepad")
        if not remaining:
            print("   All Notepad windows closed")
            return True
        else:
            print(f"   {len(remaining)} Notepad window(s) still open")
            return False
            
    except Exception as e:
        print(f"   Error closing Notepad: {e}")
        return False


def fallback_launch_notepad():
   
    print("  Launching Notepad via search...")
    
    pyautogui.press("win")
    time.sleep(0.7)
    pyautogui.typewrite("notepad")
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(2)
    
    windows = gw.getWindowsWithTitle("Notepad")
    if windows:
        print("   Notepad launched")
        return True
    else:
        print("   Fallback launch failed")
        return False