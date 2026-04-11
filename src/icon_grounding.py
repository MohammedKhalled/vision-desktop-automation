import time
import json
import os
from pathlib import Path

import pyautogui
from PIL import Image
from dotenv import load_dotenv
from botcity.core import DesktopBot
from google import genai

from src.config import RETRY_ATTEMPTS, RETRY_DELAY

load_dotenv()

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "resources" / "notepad_icon.png"


class IconGrounder(DesktopBot):
    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("GEMINI_API_KEY")

    def find_notepad_icon(self):


        # --- Stage 1: Template Matching ---
        coords = self._template_match()
        if coords:
            return coords

        # --- Stage 2: LLM Vision Fallback ---
        coords = self._llm_vision_fallback()
        if coords:
            return coords

        # Both stages exhausted — signal caller to use Windows Search
        print("   [Grounding] All vision methods failed. Caller will trigger Windows Search.")
        return None

    # -------------------------------------------------------------------------
    # Stage 1 — Template Matching
    # -------------------------------------------------------------------------

    def _template_match(self):
        if not TEMPLATE_PATH.exists():
            print(f"   [Template Matching] Skipped — template file not found: {TEMPLATE_PATH}")
            print(f"   [Template Matching] Falling through to LLM Vision.")
            return None

        print("   [Template Matching] Attempting...")
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            location = self.find(
                "notepad_icon",
                matching=0.70,
                waiting_time=1000,
            )

            if location:
                cx = location.left + location.width // 2
                cy = location.top + location.height // 2
                print(f"   [Template Matching] SUCCESS — icon found at ({cx}, {cy})")
                return cx, cy

            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)

        print("   [Template Matching] FAILED — no match after all retries.")
        print("   [Template Matching] Falling through to LLM Vision.")
        return None

    # -------------------------------------------------------------------------
    # Stage 2 — LLM Vision Fallback (Gemini)
    # -------------------------------------------------------------------------

    def _llm_vision_fallback(self):
        if not self._api_key:
            print("   [LLM Vision] Skipped — GEMINI_API_KEY not set in .env")
            return None

        print("   [LLM Vision] Attempting — capturing desktop screenshot...")

        screenshot = pyautogui.screenshot()
        img_w, img_h = screenshot.size

        screen_width, screen_height = self._get_screen_resolution()

        print(f"   [LLM Vision] Screenshot size: {img_w}x{img_h}  |  Screen size: {screen_width}x{screen_height}")


        if TEMPLATE_PATH.exists():
            template_img = Image.open(TEMPLATE_PATH)
            contents = [
                "IMAGE 1 — Reference: this is exactly the Notepad icon you are looking for.",
                template_img,
                f"IMAGE 2 — Desktop screenshot ({img_w}x{img_h} pixels): "
                "find the icon on the desktop that matches the reference above. "
                "It sits directly on the desktop (not in a taskbar or window title bar) "
                "and has the label 'Notepad' below it. "
                f"Return ONLY a raw JSON object with the pixel coordinates of its center "
                f"in this {img_w}x{img_h} image: "
                '{"x": <number>, "y": <number>}. '
                "No explanation, no markdown fences, just the JSON.",
                screenshot,
            ]
            print("   [LLM Vision] Sending template reference + screenshot to model.")
        else:
            contents = [
                f"This is a screenshot of a Windows desktop ({img_w}x{img_h} pixels). "
                "Find the Notepad desktop shortcut icon sitting directly on the desktop "
                "(not in a taskbar or window title bar). It has the label 'Notepad' below it. "
                f"Return ONLY a raw JSON object with the pixel coordinates of its center "
                f"in this {img_w}x{img_h} image: "
                '{"x": <number>, "y": <number>}. '
                "No explanation, no markdown fences, just the JSON.",
                screenshot,
            ]
            print("   [LLM Vision] Template not found — sending screenshot only.")

        try:
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
            client = genai.Client(api_key=self._api_key)

            response = client.models.generate_content(
                model=model,
                contents=contents,
            )
            text = response.text.strip()


            if "```" in text:
                text = text.split("```")[1]
                if text.lower().startswith("json"):
                    text = text[4:]
                text = text.strip()

            coords_data = json.loads(text)
            img_x = int(coords_data["x"])
            img_y = int(coords_data["y"])


            x = int(img_x * screen_width / img_w)
            y = int(img_y * screen_height / img_h)


            x = max(0, min(x, screen_width - 1))
            y = max(0, min(y, screen_height - 1))

            if img_w != screen_width or img_h != screen_height:
                print(f"   [LLM Vision] Scaled ({img_x}, {img_y}) in image → ({x}, {y}) on screen")
            print(f"   [LLM Vision] SUCCESS — Notepad located at ({x}, {y})")
            return x, y

        except json.JSONDecodeError:
            raw = response.text[:200] if response else "<no response>"
            print(f"   [LLM Vision] FAILED — model response is not valid JSON: {raw!r}")
        except Exception as e:
            print(f"   [LLM Vision] FAILED — {e}")

        print("   [LLM Vision] Falling through to Windows Search.")
        return None

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_screen_resolution(self):
        """Returns (width, height). Prefers OS-reported values; falls back to .env."""
        try:
            width, height = pyautogui.size()
            print(f"   [LLM Vision] Screen resolution (OS): {width}x{height}")
            return width, height
        except Exception as e:
            print(f"   [LLM Vision] Could not read OS resolution ({e}), checking SCREEN_RESOLUTION in .env...")

        resolution = os.getenv("SCREEN_RESOLUTION", "1920x1080")
        try:
            width, height = map(int, resolution.split("x"))
        except ValueError:
            print(f"   [LLM Vision] Invalid SCREEN_RESOLUTION value '{resolution}', defaulting to 1920x1080")
            width, height = 1920, 1080

        print(f"   [LLM Vision] Screen resolution (.env): {width}x{height}")
        return width, height
