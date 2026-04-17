import json

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


def build_region_prompt() -> str:
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


def parse_region(response_text: str, screen_w: int = 1920, screen_h: int = 1080):
    try:
        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        print("Failed to parse region response as JSON")
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
        print("Region response has invalid box dimensions")
        return None

    return x1, y1, x2, y2


def build_crop_prompt(threshold: int = 75) -> str:
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


def parse_location(response_text: str, screen_w: int = 1920, screen_h: int = 1080):
    try:
        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        print("Failed to parse location response as JSON")
        return None

    if not result.get("found"):
        print(f"Not found | confidence: {result.get('confidence')} | reason: {result.get('reason')}")
        return None

    print(f"Found | confidence: {result.get('confidence')}/100")

    pixel_x = int((result["x"] / 1000) * screen_w)
    pixel_y = int((result["y"] / 1000) * screen_h)
    return pixel_x, pixel_y
