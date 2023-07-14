# Motion Detector

This motion detector script uses OpenCV to detect and track motion in a video stream from a webcam or a video file. It identifies changes between consecutive frames and detects objects or regions that show significant movement.

## Requirements

- Python 3.x
- OpenCV (`cv2`) library
- `imutils` library
- `numpy` library
- `pandas` library
- `imageio_ffmpeg` library

## Usage

1. Ensure that you have all the required dependencies installed.
2. Copy the motion detector script into your Python environment.
3. Adjust the user-set parameters according to your preferences (explained below).
4. Run the script using a Python interpreter.

### User-Set Parameters

The following parameters can be adjusted based on your requirements:

- `COMPRESSION`: Determines the type of compression used for the saved video.
- `WIDTH` and `HEIGHT`: Determine the resolution of the saved video.
- `FRAMES_TO_PERSIST`: Number of frames to pass before changing the frame to compare the current frame against.
- `MIN_SIZE_FOR_MOVEMENT`: Minimum boxed area for detected motion to count as actual motion. This helps filter out noise or small objects.
- `MOVEMENT_DETECTED_PERSISTENCE`: Minimum length of time (in program cycles) without motion detection to declare no movement.

### Functionality

The motion detector script performs the following steps:

1. Initializes the required libraries and parameters.
2. Creates a capture object to read frames from a webcam or a video file.
3. Sets up variables for storing the first frame and the next frame to compare.
4. Opens a video writer object to save the output frames to a video file.
5. Starts a loop to continuously process frames until interrupted.
6. Reads a frame from the video stream.
7. If the frame is empty or the user presses 'q' to quit, the loop breaks, and the output is written to a data frame.
8. Resizes the frame and converts it to grayscale for better processing.
9. Blurs the grayscale image to reduce camera noise.
10. If it's the first frame, it is set as the reference frame.
11. Compares the current frame with the reference frame to find the difference.
12. Thresholds the difference image and fills in holes using morphological operations.
13. Finds contours of the thresholded image.
14. If a contour exceeds the minimum size for movement, it is considered as actual motion.
15. Draws a rectangle around regions with significant motion.
16. Updates the motion detection status and counter based on transient and persistent movement.
17. Displays the text indicating the current movement status on the frame.
18. Splices the difference frame and the original frame together for visualization.
19. Continues to the next frame.

The script will display a video window showing the processed frames with rectangles around moving objects and text indicating the current movement status. Press 'q' to stop the script.

### Output

The script will create a video file named `filename.avi` in the same directory, where the detected motion is visualized with rectangles. Additionally, it will save an Excel file named `output1.xlsx`, which contains the start and end times of each detected motion event.

> **Note**: Ensure that you have a working webcam or provide a valid video file path in the script to capture frames. The script is set up to handle both webcam input (`cap = cv2.VideoCapture(0)`) and video file input (`cap = cv2.VideoCapture('video.avi')`). Uncomment the appropriate line based on your input source.

The script is provided as-is and may require modifications or adjustments for specific use cases.

**Enjoy detecting motion with OpenCV!**
