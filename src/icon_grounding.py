import time
import os
from pathlib import Path

import pyautogui
from dotenv import load_dotenv
from botcity.core import DesktopBot
from google import genai

from src.config import RETRY_ATTEMPTS, RETRY_DELAY
from utils.screenshot import capture_desktop_with_grid

load_dotenv()

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "resources" / "notepad_icon.png"

NOTEPAD_ICON_DESCRIPTION = """
Windows 11 default Notepad icon:
- Shape       : rounded square tile (squircle), modern Win11 style
- Background  : solid sky-blue / Microsoft blue (#0078D4)
- Graphic     : white document with a folded top-right corner
- On document : faint horizontal lines (ruled paper effect)
- No text on the icon itself
- Desktop size: ~32x32 to 48x48 pixels
- Label       : the word "Notepad" centered directly below the icon
                in small white/light system font
"""


def build_notepad_prompt(threshold: int = 75) -> str:
    return f"""
IMAGE — a Windows 11 desktop screenshot.

COORDINATE SYSTEM (normalized):
- x=0 is LEFT edge,  x=1000 is RIGHT edge
- y=0 is TOP  edge,  y=1000 is BOTTOM edge

SEARCH SCOPE — desktop background only:
- ONLY look at the desktop wallpaper area.
- IGNORE the taskbar (the bar at the very bottom, y > ~930 normalized).
- IGNORE any open windows, Start menu, or system tray popups.
- Desktop icons are typically arranged in columns from the top-left
  (roughly x=0–200, y=0–900) but can be anywhere on the wallpaper.

WHAT THE NOTEPAD ICON LOOKS LIKE:
{NOTEPAD_ICON_DESCRIPTION}

HOW TO FIND IT — follow these steps in order:

Step 1 — Scan for the text label "Notepad":
  - Look across the entire desktop wallpaper for small text that reads "Notepad".
  - The label is short (7 characters), centered under its icon.
  - It is white or light-colored text on the desktop background.
  - Do NOT read labels inside the taskbar or any open window.

Step 2 — Locate the icon above the label:
  - Once you find the "Notepad" label, look directly above it.
  - The icon graphic sits immediately above the label with minimal gap.
  - The icon is a blue squircle tile with a white document graphic.

Step 3 — Verify the icon matches the description:
  - Blue/sky-blue squircle background
  - White document with a folded top-right corner
  - Faint horizontal lines on the document
  - If the icon does NOT match, do not return it — lower your confidence.

Step 4 — Pinpoint the icon center:
  - Return the center of the ICON GRAPHIC only.
  - Do NOT include the label in your center point.
  - The icon center is roughly 20–30 normalized units ABOVE the label center.

Step 5 — Score your confidence (0–100):
  - "Notepad" label is clearly readable on the desktop      → up to 35 pts
  - Icon visually matches the description above             → up to 35 pts
  - You can precisely determine the icon center coordinates → up to 30 pts
  - Deduct points if: label is partially hidden, icon is small,
    or you are not sure it is on the desktop (not the taskbar).

THRESHOLD RULE:
- confidence < {threshold}  → return not-found JSON
- confidence >= {threshold} → return coordinates JSON

OUTPUT — return ONLY a single valid JSON object, nothing else:

If found (confidence >= {threshold}):
{{"found": true, "x": 123, "y": 456, "confidence": 87}}

If not found or confidence below threshold:
{{"found": false, "confidence": 42, "reason": "Notepad label not visible on desktop"}}

STRICT RULES:
- Output the JSON object only — no markdown, no explanation, no extra text.
- Never guess a position. If unsure, lower your confidence score.
- Never return a position from the taskbar, Start menu, or any open window.
- Return the ICON center, not the label center.
"""


def parse_notepad_location(response_text: str, screen_w: int = 1920, screen_h: int = 1080):
    import json
    try:
        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        print("Failed to parse model response as JSON")
        return None

    if not result.get("found"):
        print(f"Not found | confidence: {result.get('confidence')} | reason: {result.get('reason')}")
        return None

    print(f"Found | confidence: {result.get('confidence')}/100")

    pixel_x = int((result["x"] / 1000) * screen_w)
    pixel_y = int((result["y"] / 1000) * screen_h)
    return pixel_x, pixel_y


def build_region_proposal_prompt() -> str:
    return f"""
IMAGE — a Windows 11 desktop screenshot.

TASK: Locate the approximate rectangular region that contains the Notepad icon.

WHAT THE NOTEPAD ICON LOOKS LIKE:
{NOTEPAD_ICON_DESCRIPTION}

COORDINATE SYSTEM (normalized 0–1000):
- x=0 LEFT edge,  x=1000 RIGHT edge
- y=0 TOP  edge,  y=1000 BOTTOM edge

INSTRUCTIONS:
1. Scan the desktop wallpaper only (ignore the taskbar at the very bottom, y > 930).
2. Find the area where the Notepad icon and its "Notepad" label are located.
3. Return a bounding box that generously encloses both the icon and label with ~50 units of padding on each side.

OUTPUT — return ONLY a single valid JSON object:

If region found (confidence >= 50):
{{"found": true, "x1": 10, "y1": 20, "x2": 150, "y2": 120, "confidence": 80}}

If not found:
{{"found": false, "confidence": 25, "reason": "No Notepad icon visible on desktop"}}

Rules:
- JSON only — no markdown, no explanation, no extra text.
- confidence < 50 → return not-found JSON.
- x1 < x2 and y1 < y2.
"""


def parse_region_proposal(response_text: str, screen_w: int = 1920, screen_h: int = 1080):
    import json
    try:
        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        print("Failed to parse region proposal as JSON")
        return None

    if not result.get("found"):
        print(f"Region not found | confidence: {result.get('confidence')} | reason: {result.get('reason')}")
        return None

    print(f"Region found | confidence: {result.get('confidence')}/100")

    x1 = max(0, int((result["x1"] / 1000) * screen_w))
    y1 = max(0, int((result["y1"] / 1000) * screen_h))
    x2 = min(screen_w, int((result["x2"] / 1000) * screen_w))
    y2 = min(screen_h, int((result["y2"] / 1000) * screen_h))

    if x2 <= x1 or y2 <= y1:
        print("Region proposal returned invalid box dimensions")
        return None

    return x1, y1, x2, y2


def build_precise_grounding_prompt(threshold: int = 75) -> str:
    return f"""
IMAGE — a cropped region of a Windows 11 desktop, zoomed in.

TASK: Find the exact center of the Notepad icon graphic in this cropped image.

WHAT THE NOTEPAD ICON LOOKS LIKE:
{NOTEPAD_ICON_DESCRIPTION}

COORDINATE SYSTEM (normalized 0–1000 within THIS image only):
- x=0 is the LEFT edge of this image,  x=1000 is the RIGHT edge
- y=0 is the TOP  edge of this image,  y=1000 is the BOTTOM edge

INSTRUCTIONS:
Step 1 — Find the "Notepad" text label anywhere in this image.
Step 2 — Look directly above the label for the blue squircle icon graphic.
Step 3 — Verify it matches the description (blue background, white document with folded corner).
Step 4 — Return the center of the ICON GRAPHIC only — not the label center.
Step 5 — Score your confidence (0–100):
  - Label clearly readable                    → up to 35 pts
  - Icon matches description                  → up to 35 pts
  - Center precisely determinable             → up to 30 pts

THRESHOLD RULE:
- confidence < {threshold}  → return not-found JSON
- confidence >= {threshold} → return coordinates JSON

OUTPUT — return ONLY a single valid JSON object:

If found (confidence >= {threshold}):
{{"found": true, "x": 500, "y": 300, "confidence": 92}}

If not found:
{{"found": false, "confidence": 20, "reason": "Notepad icon not visible in this region"}}

Rules: JSON only, no markdown, no explanation.
"""


class IconGrounder(DesktopBot):
    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("GEMINI_API_KEY")

    def find_notepad_icon(self):


        # --- Stage 1: Template Matching ---
        #coords = self._template_match()
        #if coords:
        #    return coords

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

        # Save debug grid screenshot (unchanged)
        grid_screenshot = capture_desktop_with_grid(grid_size=100)
        save_path = Path("notepad_screenshots")
        save_path.mkdir(parents=True, exist_ok=True)
        filename = save_path / f"grid_screenshot_.png"
        grid_screenshot.save(filename)
        print(f"Saved screenshot to: {filename}")

        screen_width, screen_height = self._get_screen_resolution()

        # Clean screenshot for model calls (no grid overlay)
        clean_screenshot = pyautogui.screenshot()
        img_w, img_h = clean_screenshot.size
        print(f"   [LLM Vision] Screenshot size: {img_w}x{img_h}  |  Screen size: {screen_width}x{screen_height}")

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        client = genai.Client(api_key=self._api_key)

        try:
            # --- ScreenSeekeR Stage 1: Region Proposal ---
            # Ask the model for a rough bounding box so we can zoom in.
            # A 40px icon is tiny at 1920×1080; cropping it out makes it
            # much larger in the model's viewport → higher precision.
            print("   [LLM Vision] Stage 1 — proposing search region on full screenshot...")
            region_response = client.models.generate_content(
                model=model_name,
                contents=[clean_screenshot, build_region_proposal_prompt()],
            )
            region = parse_region_proposal(
                region_response.text.strip(),
                screen_w=screen_width,
                screen_h=screen_height,
            )

            if region:
                x1, y1, x2, y2 = region
                print(f"   [LLM Vision] Stage 1 SUCCESS — region: ({x1}, {y1}) → ({x2}, {y2})")

                # --- ScreenSeekeR Stage 2: Precise Grounding in Cropped Region ---
                crop = clean_screenshot.crop((x1, y1, x2, y2))
                crop_w, crop_h = crop.size
                print(f"   [LLM Vision] Stage 2 — precise grounding in {crop_w}x{crop_h} crop...")

                precise_response = client.models.generate_content(
                    model=model_name,
                    contents=[crop, build_precise_grounding_prompt()],
                )
                rel_coords = parse_notepad_location(
                    precise_response.text.strip(),
                    screen_w=crop_w,
                    screen_h=crop_h,
                )

                if rel_coords:
                    # rel_coords are pixel offsets within the crop; add crop origin
                    abs_x = x1 + rel_coords[0]
                    abs_y = y1 + rel_coords[1]
                    print(f"   [LLM Vision] SUCCESS — Notepad located at ({abs_x}, {abs_y})")
                    return abs_x, abs_y

                print("   [LLM Vision] Stage 2 failed — falling back to direct grounding.")
            else:
                print("   [LLM Vision] Stage 1 failed — falling back to direct grounding.")

            # --- Fallback: Direct Grounding on Full Screenshot ---
            print("   [LLM Vision] Fallback — direct grounding on full screenshot...")
            direct_response = client.models.generate_content(
                model=model_name,
                contents=[clean_screenshot, build_notepad_prompt()],
            )
            coords = parse_notepad_location(
                direct_response.text.strip(),
                screen_w=screen_width,
                screen_h=screen_height,
            )
            if coords is None:
                print("   [LLM Vision] FAILED — icon not found or confidence too low.")
            else:
                x, y = coords
                print(f"   [LLM Vision] SUCCESS — Notepad located at ({x}, {y})")
                return x, y

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
