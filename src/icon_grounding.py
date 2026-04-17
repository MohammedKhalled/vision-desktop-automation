import time
import os
from pathlib import Path

import pyautogui
from dotenv import load_dotenv
from botcity.core import DesktopBot
from google import genai

from src.config import RETRY_ATTEMPTS, RETRY_DELAY, GEMINI_MODELS
from utils.screenshot import capture_desktop_with_grid
from utils.llm_utils import build_region_prompt, parse_region, build_crop_prompt, parse_location

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

        # --- Stage 2: LLM Vision ---
        coords = self._llm_vision_fallback()
        if coords:
            return coords

        print("   [Grounding] All methods failed. Caller will trigger Windows Search.")
        return None

    # -------------------------------------------------------------------------
    # Stage 1 — Template Matching
    # -------------------------------------------------------------------------

    def _template_match(self):
        if not TEMPLATE_PATH.exists():
            print(f"   [Template] Skipped — template not found: {TEMPLATE_PATH}")
            return None

        print("   [Template] Attempting...")
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            location = self.find(
                "notepad_icon",
                matching=0.90,
                waiting_time=1000,
            )
            
            # Click on the center of the icon
            if location:
                cx = location.left + location.width // 2
                cy = location.top + location.height // 2
                print(f"   [Template] SUCCESS — icon at ({cx}, {cy})")
                return cx, cy

            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)

        print("   [Template] FAILED — no match after all retries.")
        return None

    # -------------------------------------------------------------------------
    # Stage 2 — LLM Vision Fallback (Gemini)
    # -------------------------------------------------------------------------

    def _llm_vision_fallback(self):
        if not self._api_key:
            print("   [Vision] Skipped — GEMINI_API_KEY not set in .env")
            return None

        print("   [Vision] Capturing screenshot...")
        screen_w, screen_h = self._get_screen_resolution()

        screenshot = pyautogui.screenshot()
        img_w, img_h = screenshot.size
        print(f"   [Vision] Screenshot: {img_w}x{img_h} | Screen: {screen_w}x{screen_h}")

        client = genai.Client(api_key=self._api_key)

        for model_name in GEMINI_MODELS:
            print(f"   [Vision] Trying model: {model_name}")

            for attempt in range(1, RETRY_ATTEMPTS + 1):
                try:
                    print(f"   [Vision] Attempt {attempt}/{RETRY_ATTEMPTS} — Stage 1: finding region...")
                    region_response = client.models.generate_content(
                        model=model_name,
                        contents=[screenshot, build_region_prompt()],
                    )
                    region = parse_region(region_response.text.strip(), screen_w=screen_w, screen_h=screen_h)

                    if region is None:
                        print(f"   [Vision] Attempt {attempt} — Stage 1 failed, region not found.")
                        continue

                    x1, y1, x2, y2 = region
                    print(f"   [Vision] Stage 1 SUCCESS — region: ({x1}, {y1}) → ({x2}, {y2})")

                    print(f"   [Vision] Attempt {attempt}/{RETRY_ATTEMPTS} — Stage 2: locating icon in crop...")
                    crop = screenshot.crop((x1, y1, x2, y2))
                    crop_w, crop_h = crop.size

                    precise_response = client.models.generate_content(
                        model=model_name,
                        contents=[crop, build_crop_prompt()],
                    )
                    rel_coords = parse_location(precise_response.text.strip(), screen_w=crop_w, screen_h=crop_h)

                    if rel_coords is None:
                        print(f"   [Vision] Attempt {attempt} — Stage 2 failed, icon not found in crop.")
                        continue

                    abs_x = x1 + rel_coords[0]
                    abs_y = y1 + rel_coords[1]
                    print(f"   [Vision] SUCCESS — Notepad at ({abs_x}, {abs_y})")
                    return abs_x, abs_y

                except Exception as e:
                    print(f"   [Vision] Attempt {attempt} failed with model '{model_name}' — {e}")
                    if attempt == RETRY_ATTEMPTS:
                        print(f"   [Vision] All retries exhausted for model '{model_name}', trying next model.")

        print("   [Vision] All models failed.")
        return None

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_screen_resolution(self):
        try:
            width, height = pyautogui.size()
            print(f"   [Vision] Screen size (OS): {width}x{height}")
            return width, height
        except Exception as e:
            print(f"   [Vision] OS screen size failed ({e}), checking .env...")

        resolution = os.getenv("SCREEN_RESOLUTION", "1920x1080")
        try:
            width, height = map(int, resolution.split("x"))
        except ValueError:
            print(f"   [Vision] Invalid SCREEN_RESOLUTION '{resolution}', defaulting to 1920x1080")
            width, height = 1920, 1080

        print(f"   [Vision] Screen size (.env): {width}x{height}")
        return width, height
