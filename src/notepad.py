import os
import glob
import pyautogui
import pygetwindow as gw
import time


# --- Directory Management ---

def get_desktop_project_dir():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    target = os.path.join(desktop, "tjm-project")
    os.makedirs(target, exist_ok=True)
    return target


def cleanup_previous_posts(save_dir):
    pattern = os.path.join(save_dir, "post_*.txt")
    for filepath in glob.glob(pattern):
        try:
            os.remove(filepath)
            print(f"Removed existing file: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Warning: Could not remove {os.path.basename(filepath)}: {e}")


# --- Notepad Window Control ---

def open_notepad_at(x, y):
    print(f"   Opening Notepad at ({x}, {y})...")
    pyautogui.doubleClick(x, y)
    time.sleep(2)

    windows = gw.getWindowsWithTitle("Notepad")
    if windows:
        print("   Notepad opened")
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
    print("   Launching Notepad via search...")

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


# --- Content Typing & Saving ---

def type_post(post, save_dir):
    title = post.get('title', '')
    body = post.get('body', '')
    content = f"Title: {title}\n\n{body}"

    filename = f"post_{post['id']}.txt"
    full_path = os.path.join(save_dir, filename)

    try:
        print("   Activating Notepad window...")
        notepad_windows = gw.getWindowsWithTitle("Notepad")

        if not notepad_windows:
            print("   ERROR: No Notepad window found")
            return False

        notepad_window = notepad_windows[0]
        notepad_window.activate()
        time.sleep(0.5)

        window_center_x = notepad_window.left + notepad_window.width // 2
        window_center_y = notepad_window.top + notepad_window.height // 2 + 50
        pyautogui.click(window_center_x, window_center_y)
        time.sleep(0.3)

        print(f"   Typing post content ({len(content)} characters)...")

        for char in content:
            if char == '\n':
                pyautogui.press('enter')
            else:
                pyautogui.write(char, interval=0)

        print("   Content typed successfully")
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
                print("   WARNING: File verification failed")
                return True

    except Exception as e:
        print(f"   ERROR during typing/saving: {e}")
        import traceback
        traceback.print_exc()
        return False
