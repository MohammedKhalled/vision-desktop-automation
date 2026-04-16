import pyautogui
import cv2
import numpy as np
from PIL import ImageDraw, ImageFont


def capture_desktop():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img


def capture_desktop_with_grid(grid_size=100):
    screenshot = pyautogui.screenshot()

    grid_img = screenshot.copy()
    draw = ImageDraw.Draw(grid_img)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    # Vertical lines + labels
    for x in range(0, grid_img.width, grid_size):
        draw.line([(x, 0), (x, grid_img.height)], fill="red", width=2)

        label = f"x={x}"
        text_x = min(x + 5, grid_img.width - 80)

        draw.rectangle(
            [(text_x - 2, 0), (text_x + 75, 35)],
            fill="black"
        )
        draw.text((text_x, 5), label, fill="red", font=font)

    # Horizontal lines + labels
    for y in range(0, grid_img.height, grid_size):
        draw.line([(0, y), (grid_img.width, y)], fill="red", width=2)

        label = f"y={y}"
        text_y = min(y + 5, grid_img.height - 35)

        draw.rectangle(
            [(0, text_y - 2), (90, text_y + 30)],
            fill="black"
        )
        draw.text((5, text_y), label, fill="red", font=font)

    return grid_img