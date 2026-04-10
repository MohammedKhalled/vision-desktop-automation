from botcity.core import DesktopBot
import time
from src.config import RETRY_ATTEMPTS, RETRY_DELAY


class IconGrounder(DesktopBot):
    def __init__(self):
        super().__init__()

    def find_notepad_icon(self):
        for _ in range(RETRY_ATTEMPTS):
            location = self.find(
                "notepad_icon",
                matching=0.70,      
                waiting_time=1000
            )

            if location:
                cx = location.left + location.width // 2
                cy = location.top + location.height // 2
                return cx, cy

            time.sleep(RETRY_DELAY)

        return None