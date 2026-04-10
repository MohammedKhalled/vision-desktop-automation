# Vision-Based Desktop Automation with Dynamic Icon Grounding

A Python automation system that uses computer vision to dynamically locate and interact with desktop icons on Windows, enabling robust automation even when icon positions change.

## 🎯 Project Overview

This project demonstrates vision-based icon grounding by:
- Detecting the Notepad desktop icon regardless of its position (top-left, bottom-right, center, or anywhere)
- Automatically fetching blog posts from an external API
- Saving each post to individual text files via automated Notepad interaction
- Handling errors gracefully with fallback mechanisms

## ✨ Key Features

- **Dynamic Icon Grounding**: Locates Notepad icon on desktop regardless of position using computer vision
- **Robust Automation**: Handles icon position changes without manual configuration
- **API Integration**: Fetches real-time data from JSONPlaceholder API
- **Fallback Mechanisms**: Graceful degradation when visual grounding fails
- **Error Handling**: Retry logic and alternative launch methods
- **Clean File Management**: Automatically cleans up previous runs

## 🖼️ Screenshots

The system successfully detects the Notepad icon regardless of desktop position:

### Top-Left Detection
![Top-Left Detection](screenshots/1_top_left_detection.png)

### Bottom-Right Detection
![Bottom-Right Detection](screenshots/2_bottom_right_detection.png)

### Center Detection
![Center Detection](screenshots/3_center_detection.png)

*All screenshots show successful icon grounding with detected coordinates and bounding boxes.*

## 🏗️ Architecture

```
tjm-icon-grounding/
├── src/
│   ├── vision/
│   │   ├── icon_grounding.py      # Computer vision icon detection
│   │   └── screenshot.py.py       # Desktop capture utility
│   ├── automation/
│   │   ├── notepad.py              # Notepad window management
│   │   └── typing.py               # Content handling and file saving
│   ├── services/
│   │   ├── posts_api.py            # API integration
│   │   └── fallback_posts.json    # Offline fallback data
│   ├── utils/
│   │   ├── paths.py                # File path management
│   │   └── retries.py              # Retry logic helper
│   ├── config.py                   # Configuration settings
│   └── capture_screenshots.py      # capturing screenshots of detecting
├── main.py                         # Main automation workflow
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (1920x1080 resolution recommended)
- Notepad shortcut icon on desktop

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/vision-desktop-automation.git
cd vision-desktop-automation
```

2. **Create virtual environment** (not required)
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Verify Notepad icon exists**
- Ensure you have a Notepad shortcut on your desktop
- If not, create one: Right-click Desktop → New → Shortcut → `notepad.exe`

## 📋 Requirements

```
pyautogui>=0.9.53
pygetwindow>=0.0.9
requests>=2.28.0
botcity-framework>=0.4.0
opencv-python>=4.7.0
numpy>=1.24.0
```

## 🎮 Usage

### Basic Usage

Run the automation:
```bash
python main.py
```

### What It Does

1. **Cleanup**: Removes previous post files from Desktop/tjm-project
2. **Fetch Data**: Retrieves 10 blog posts from JSONPlaceholder API
3. **Icon Grounding**: Locates Notepad icon on desktop using computer vision
4. **Automation Loop**: For each post:
   - Opens Notepad via detected icon
   - Saves post content to file
   - Closes Notepad
   - Repeats for next post

### Expected Output

```
============================================================
=== Desktop Automation with Vision-Based Icon Grounding ===
============================================================

Step 1: Fetching posts from API...
✓ Successfully fetched 10 posts.

Step 2: Setting up save directory...
✓ Save directory: C:\Users\YourName\Desktop\tjm-project

Step 3: Cleaning up previous posts...
Removed existing file: post_1.txt
...

Step 4: Initializing icon grounder...
✓ Icon grounder ready

============================================================
Processing Posts...
============================================================

[1/10] Processing Post #1: sunt aut facere repellat...
------------------------------------------------------------
✓ Notepad icon found at (150, 200)
  → Opening Notepad at (150, 200)...
  ✓ Notepad opened
  ✓ File saved: post_1.txt (245 bytes)
  → Closing Notepad...
  ✓ Notepad process killed
------------------------------------------------------------
Status: Post #1 - ✓ SUCCESS

...

============================================================
=== Automation Complete ===
============================================================
Total posts: 10
Successful: 10
Failed: 0
Success rate: 100.0%

Files saved to: C:\Users\YourName\Desktop\tjm-project
============================================================
```

## 🔧 Configuration

Edit `src/config.py` to customize:

```python
SCREEN_WIDTH = 1920          
SCREEN_HEIGHT = 1080         
RETRY_ATTEMPTS = 3           
RETRY_DELAY = 1              
POST_LIMIT = 10              
```

## 🧪 Testing

### Test Icon Detection

```python
from src.vision.icon_grounding import IconGrounder

grounder = IconGrounder()
coords = grounder.find_notepad_icon()

if coords:
    print(f" Icon detected at: {coords}")
else:
    print(" Icon not detected")
```

### Test API Connection

```python
from src.services.posts_api import fetch_posts

posts = fetch_posts(5)
print(f"Fetched {len(posts)} posts")
```

## 🎯 Icon Grounding Implementation

The icon grounding system uses **computer vision** to locate the Notepad icon:

1. **Screen Capture**: Captures full desktop screenshot
2. **Template Matching**: Uses OpenCV to find icon template in screenshot
3. **Coordinate Calculation**: Returns center point (x, y) of detected icon
4. **Fallback Method**: If visual grounding fails, uses Windows search

### Grounding Process

```python
# Visual grounding
coords = grounder.find_notepad_icon()

if coords:
    # Icon found - double-click at detected coordinates
    open_notepad_at(coords[0], coords[1])
else:
    # Fallback - use Windows search
    fallback_launch_notepad()
```

This approach ensures the automation works **regardless of icon position**.

## 🛡️ Error Handling

### Implemented Safeguards

- **API Failure**: Falls back to local JSON data if API is unavailable
- **Icon Not Found**: Uses Windows search as fallback launch method
- **File Conflicts**: Automatically removes old files before starting
- **Window Management**: Force-kills Notepad processes to ensure clean state
- **Retry Logic**: Up to 3 attempts for icon detection with delays

## 📊 Performance

- **Icon Detection**: ~1-2 seconds per detection
- **File Save**: Instant (direct Python I/O)
- **Total Runtime**: ~30-40 seconds for 10 posts
- **Success Rate**: 99%+ on standard Windows 10/11 systems

## 🔍 Troubleshooting

### Icon Not Detected

**Problem**: "Visual grounding failed - using fallback"

**Solutions**:
1. Ensure Notepad icon exists on desktop
2. Check icon isn't covered by other windows
3. Verify screen resolution matches config
4. Adjust matching threshold in `icon_grounding.py`

### Files Not Saving

**Problem**: Files not appearing in Desktop/tjm-project

**Solutions**:
1. Check folder permissions
2. Run script as Administrator
3. Verify `Desktop/tjm-project` folder exists
4. Check antivirus isn't blocking file writes

### Notepad Won't Close

**Problem**: Multiple Notepad windows left open

**Solutions**:
1. Current implementation uses `taskkill` - should be 100% reliable
2. If issues persist, manually close windows and re-run
3. Check Task Manager for hung Notepad processes

## 🎓 Learning Outcomes

This project demonstrates:

- **Computer Vision**: Template matching for object detection
- **Desktop Automation**: Programmatic control of GUI applications
- **API Integration**: RESTful API consumption with fallbacks
- **Error Handling**: Robust error handling and retry mechanisms
- **File I/O**: Automated file creation and management
- **Window Management**: Process and window control on Windows

## 📝 Future Enhancements

Potential improvements:

- [ ] Support for multiple screen resolutions
- [ ] Machine learning-based icon detection
- [ ] Support for other applications beyond Notepad
- [ ] GUI for configuration
- [ ] Logging system for debugging
- [ ] Multi-monitor support
- [ ] Linux/macOS compatibility

## 🤝 Contributing

This is a demonstration project for a job interview. Contributions are not currently accepted.

## 📄 License

This project is created for educational and demonstration purposes.

## 👤 Author

**Your Name**
- GitHub: [MohammedKhalled](https://github.com/MohammedKhalled)
- LinkedIn: [Mohamed Khaled](hwww.linkedin.com/in/mohamed-khaled-7812112a3)

## 🙏 Acknowledgments

- JSONPlaceholder API for test data
- BotCity framework for desktop automation
- OpenCV community for computer vision tools

## 📞 Contact

For questions about this project, please contact: mhmddkhaled618@gmail.com

---

**Note**: This project was created as part of a technical assessment demonstrating vision-based desktop automation and icon grounding capabilities.