# Hand Gesture Control System

A Python application that allows you to control your computer's brightness and volume using hand gestures captured through your webcam.

## Features

- **Brightness Control**: Use your left hand to control screen brightness
- **Volume Control**: Use your right hand to control system volume
- **Real-time Hand Tracking**: Advanced hand gesture recognition using MediaPipe
- **Modern UI**: Clean, intuitive interface with progress bars and icons
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

### Python Version
**Important**: This application requires Python 3.8, 3.9, or 3.10 for optimal compatibility. Python 3.11+ may have issues with some dependencies.

### System Requirements
- Webcam
- Windows OS (for volume control via pycaw)
- Sufficient lighting for hand detection

## Installation

### Step 1: Install Python
1. Download and install Python 3.10 from [python.org](https://www.python.org/downloads/)
2. Make sure to check "Add Python to PATH" during installation

### Step 2: Clone or Download the Project
```bash
git clone <repository-url>
cd mini
```

### Step 3: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
python main.PY
```

### How to Use
1. **Launch the application** - The webcam feed will open in a window
2. **Position your hands**:
   - **Left hand**: Control screen brightness
   - **Right hand**: Control system volume
3. **Gesture Control**:
   - Extend your thumb and index finger
   - Adjust the distance between them to control values
   - Closer fingers = lower values
   - Further apart = higher values
4. **Exit**: Click the "Exit" button or close the window

### Controls
- **Brightness**: 0-100% (controlled by left hand)
- **Volume**: 0-100% (controlled by right hand)
- **Visual Feedback**: Progress bars show current values in real-time

## Troubleshooting

### Common Issues

1. **"No module named 'cv2'"**
   - Solution: Install OpenCV: `pip install opencv-python`

2. **"No module named 'mediapipe'"**
   - Solution: Ensure you're using Python 3.8-3.10 and reinstall: `pip install mediapipe==0.10.7`

3. **Webcam not detected**
   - Solution: Check webcam permissions and ensure no other application is using it

4. **Volume control not working (Windows)**
   - Solution: Run as administrator or check audio device settings

5. **Brightness control not working**
   - Solution: Ensure you have proper permissions and compatible display drivers

### Python Version Issues
If you're using Python 3.11+ and encounter issues:
1. Install Python 3.10
2. Create a new virtual environment with Python 3.10
3. Reinstall dependencies

## Dependencies

- **opencv-python**: Computer vision and webcam capture
- **numpy**: Numerical computing
- **mediapipe**: Hand tracking and gesture recognition
- **screen-brightness-control**: Screen brightness manipulation
- **pycaw**: Windows audio control
- **comtypes**: COM interface for Windows
- **Pillow**: Image processing for UI

## File Structure

```
mini/
├── main.PY              # Main application file
├── new.py               # Alternative version (same as main.PY)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues, please check the troubleshooting section above or create an issue in the repository. 