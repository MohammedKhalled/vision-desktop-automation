import cv2
import os
from datetime import datetime
from src.vision.icon_grounding import IconGrounder
from src.vision.screenshot import capture_desktop


def annotate_screenshot(img, icon_coords, position_name, output_dir):


    annotated = img.copy()
    
    if icon_coords:
        x, y = icon_coords
        

        cv2.circle(annotated, (x, y), 10, (0, 255, 0), 3)
        

        box_size = 64  
        top_left = (x - box_size//2, y - box_size//2)
        bottom_right = (x + box_size//2, y + box_size//2)
        cv2.rectangle(annotated, top_left, bottom_right, (0, 255, 0), 3)
        

        label = f"Notepad Icon Detected: ({x}, {y})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        font_thickness = 3
        
 
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, font_thickness
        )
        

        label_x = x - text_width // 2
        label_y = y - box_size//2 - 20
        

        if label_y < text_height + 10:
            label_y = y + box_size//2 + text_height + 20
        if label_x < 10:
            label_x = 10
        if label_x + text_width > img.shape[1] - 10:
            label_x = img.shape[1] - text_width - 10
        

        cv2.rectangle(
            annotated,
            (label_x - 10, label_y - text_height - 10),
            (label_x + text_width + 10, label_y + baseline + 10),
            (0, 0, 0),
            -1
        )
        

        cv2.putText(
            annotated,
            label,
            (label_x, label_y),
            font,
            font_scale,
            (0, 255, 0),
            font_thickness
        )
        

        position_label = f"Position: {position_name.upper()}"
        cv2.putText(
            annotated,
            position_label,
            (20, 50),
            font,
            1.0,
            (255, 255, 0),
            2
        )
        

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            annotated,
            timestamp,
            (20, img.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
    else:

        cv2.putText(
            annotated,
            "ERROR: Notepad Icon Not Detected!",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 0, 255),
            3
        )
    

    filename = f"notepad_detection_{position_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    
    cv2.imwrite(filepath, annotated)
    print(f" Screenshot saved: {filepath}")
    
    return filepath


def capture_and_annotate(position_name, output_dir):

    print(f"\n{'='*60}")
    print(f"Capturing screenshot for: {position_name.upper()}")
    print(f"{'='*60}")
    

    print("Initializing icon grounder...")
    grounder = IconGrounder()
    

    print("Capturing desktop screenshot...")
    screenshot = capture_desktop()
    

    print("Detecting Notepad icon...")
    coords = grounder.find_notepad_icon()
    
    if coords:
        print(f" Icon detected at coordinates: ({coords[0]}, {coords[1]})")
    else:
        print(" WARNING: Icon not detected!")
    

    print("Annotating screenshot...")
    filepath = annotate_screenshot(screenshot, coords, position_name, output_dir)
    
    return filepath, coords


def main():
  
    print("="*60)
    print("Notepad Icon Detection - Screenshot Annotation Tool")
    print("="*60)
    print()
    

    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "notepad_screenshots")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Screenshots will be saved to: {output_dir}\n")
    

    print("INSTRUCTIONS:")
    print("1. This script will capture 3 screenshots")
    print("2. Before each capture, move your Notepad icon to the specified position")
    print("3. Press Enter when ready for each capture")
    print()
    
    positions = [
        ("top-left", "Move Notepad icon to TOP-LEFT area of desktop"),
        ("bottom-right", "Move Notepad icon to BOTTOM-RIGHT area of desktop"),
        ("center", "Move Notepad icon to CENTER of desktop")
    ]
    
    results = []
    
    for position_name, instruction in positions:
        print(f"\n{instruction}")
        input("Press Enter when ready to capture...")
        
        filepath, coords = capture_and_annotate(position_name, output_dir)
        results.append({
            'position': position_name,
            'filepath': filepath,
            'coords': coords,
            'success': coords is not None
        })
        
        if coords:
            print(f" {position_name} screenshot complete!")
        else:
            print(f" {position_name} screenshot captured but icon not detected!")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        status = " SUCCESS" if result['success'] else " FAILED"
        coords_str = f"({result['coords'][0]}, {result['coords'][1]})" if result['coords'] else "Not detected"
        print(f"{i}. {result['position']:15s} - {status:15s} - Coords: {coords_str}")
        print(f"   File: {os.path.basename(result['filepath'])}")
    
    print(f"\nAll screenshots saved to: {output_dir}")
    print("\nYou can now include these annotated screenshots in your project documentation!")


if __name__ == "__main__":
    main()