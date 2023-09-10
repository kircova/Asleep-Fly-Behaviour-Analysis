import imutils
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from imageio_ffmpeg import write_frames

# =============================================================================
# USER-SET PARAMETERS
# =============================================================================

# Set the video compression type for the saved video (e.g., H264)
COMPRESSION = "H264"

# Set the width and height of the saved video frame
WIDTH = 1080
HEIGHT = 720

# Number of frames to wait before comparing to the current frame
FRAMES_TO_PERSIST = 10

# Minimum area required for detected motion to be considered valid
MIN_SIZE_FOR_MOVEMENT = 100

# Minimum duration without motion to declare that there's no movement
MOVEMENT_DETECTED_PERSISTENCE = 100

# =============================================================================

# Create a capture object for video input
cap = cv2.VideoCapture(0)  # Initialize the webcam
# cap = cv2.VideoCapture('video.avi')
## vs = cv2.VideoCapture(args["video"])

# Initialize variables for previous and current frames
first_frame = None
next_frame = None

# Initialize display font and counters
font = cv2.FONT_HERSHEY_SIMPLEX
delay_counter = 0
movement_persistent_counter = 0

# Additional variables by Yusufhan Kircova
previously_moving = False
motion_Event_List = []
motion_Event = []

# Get frame dimensions and create a VideoWriter object to save the output video
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
size = (frame_width, frame_height)
result = cv2.VideoWriter('filename.avi', cv2.VideoWriter_fourcc(*COMPRESSION), 10, size)

# Main video processing loop
while True:

    # Set transient motion detected as false
    transient_movement_flag = False

    # Read a frame from the video source
    ret, frame = cap.read()
    text = "Unoccupied"

    # Check for user interruption (press 'q' to quit) or if the frame is empty
    ch = cv2.waitKey(1)
    if frame is None or ch & 0xFF == ord('q'):
        print(motion_Event_List)
        columns = ['Sleep State Start', 'Sleep State Ended ']
        df = pd.DataFrame(motion_Event_List, columns=columns)
        df.to_excel('output1.xlsx')
        break

    # If there's an error in capturing, continue
    if not ret:
        print("CAPTURE ERROR")
        continue

    # Write the frame to the output video
    result.write(frame)

    # Resize the frame and convert it to grayscale
    frame = imutils.resize(frame, width=WIDTH, height=HEIGHT)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # If the first frame is None, initialize it
    if first_frame is None:
        first_frame = gray

    delay_counter += 1

    # Set the first frame to compare as the previous frame after a delay
    if delay_counter > FRAMES_TO_PERSIST:
        delay_counter = 0
        first_frame = next_frame

    # Set the next frame to compare (the current frame)
    next_frame = gray

    # Compare the two frames to find the difference
    frame_delta = cv2.absdiff(first_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # Fill in holes via dilate() and find contours of the thresholds
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, b) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over the contours
    for c in cnts:

        # Save the coordinates of all found contours
        (x, y, w, h) = cv2.boundingRect(c)

        # Check if the contour is large enough to be considered as motion
        if cv2.contourArea(c) > MIN_SIZE_FOR_MOVEMENT:
            if not previously_moving:
                endtime = datetime.now()
                print("No Motion State Ended - Fly Awake", endtime.strftime('%Y-%m-%d %H:%M:%S'), "\n")
                motion_Event.append(endtime.strftime('%Y-%m-%d %H:%M:%S'))
                motion_Event_List.append(motion_Event)
                motion_Event = []
                previously_moving = True

            transient_movement_flag = True
            # Draw a rectangle around large enough movements
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Reset the persistent movement timer if something moves momentarily
    if transient_movement_flag:
        movement_persistent_flag = True
        movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE

    # If there was recent transient movement, display it
    if movement_persistent_counter > 1:
        text = "Movement Detected " + str(movement_persistent_counter)
        movement_persistent_counter -= 1
    elif movement_persistent_counter == 1:
        starttime = datetime.now()
        print("No Motion State Started - Fly Asleep", starttime.strftime('%Y-%m-%d %H:%M:%S'))
        motion_Event.append(starttime.strftime('%Y-%m-%d %H:%M:%S'))
        movement_persistent_counter -= 1
        previously_moving = False
    else:
        text = "No Movement Detected"

    # Display the text on the screen and show the video frames
    cv2.putText(frame, str(text), (10, 35), font, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

    # For showing individual video frames
    # cv2.imshow("frame", frame)
    # cv2.imshow("delta", frame_delta)

    # Convert the frame_delta to color for splicing
    frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR)

    # Splice the two video frames together horizontally
    cv2.imshow("frame", np.hstack((frame_delta, frame)))

# Cleanup when closed
cv2.waitKey(0)
cv2.destroyAllWindows()
cap.release()
result.release()
