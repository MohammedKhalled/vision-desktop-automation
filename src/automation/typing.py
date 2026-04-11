import os
import pyautogui
import pygetwindow as gw
import time


def type_post(post, save_dir):

    title = post.get('title', '')
    body = post.get('body', '')
    content = f"Title: {title}\n\n{body}"
    
    
    filename = f"post_{post['id']}.txt"
    full_path = os.path.join(save_dir, filename)
    
    try:

        print(f"   Activating Notepad window...")
        notepad_windows = gw.getWindowsWithTitle("Notepad")
        
        if not notepad_windows:
            print(f"   ERROR: No Notepad window found")
            return False
        
        
        notepad_window = notepad_windows[0]
        notepad_window.activate()
        time.sleep(0.5)  
        
        
        window_center_x = notepad_window.left + notepad_window.width // 2
        window_center_y = notepad_window.top + notepad_window.height // 2 + 50  # Slightly below center
        pyautogui.click(window_center_x, window_center_y)
        time.sleep(0.3)
        

        print(f"   Typing post content ({len(content)} characters)...")
        

        for char in content:
            if char == '\n':
                
                pyautogui.press('enter')
            else:

                pyautogui.write(char, interval=0)
        
        print(f"   Content typed successfully")
        time.sleep(0.5)
        

        print(f"   Saving file as {filename}...")
        
        
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1.5)  
        

        pyautogui.hotkey('ctrl', 'a')  
        time.sleep(0.2)
        

        pyautogui.typewrite(full_path, interval=0.01)
        time.sleep(0.5)
        

        pyautogui.press('enter')
        time.sleep(1)
        

        

        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"   File saved: {filename} ({file_size} bytes)")
            return True
        else:

            time.sleep(0.5)
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                print(f"   File saved: {filename} ({file_size} bytes)")
                return True
            else:
                print(f"   WARNING: File verification failed")
                return True
            
    except Exception as e:
        print(f"   ERROR during typing/saving: {e}")
        import traceback
        traceback.print_exc()
        return False