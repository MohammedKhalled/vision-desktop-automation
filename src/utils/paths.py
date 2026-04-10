import os
import glob

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