import imutils
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from imageio_ffmpeg import write_frames

# =============================================================================
# USER-SET PARAMETERS
# =============================================================================
# Determines which type of compression will be used on saved video
COMPRESSION =  "H264"
# Determines which type of resolution of saved video
WIDTH = 1080
HEIGHT = 720

# Number of frames to pass before changing the frame to compare the current
# frame against
FRAMES_TO_PERSIST = 10

# Minimum boxed area for a detected motion to count as actual motion
# Use to filter out noise or small objects
MIN_SIZE_FOR_MOVEMENT = 100

# Minimum length of time where no motion is detected it should take
#(in program cycles) for the program to declare that there is no movement
MOVEMENT_DETECTED_PERSISTENCE = 100

# =============================================================================

# Create capture object
# Minor fix
cap = cv2.VideoCapture(0) # Then start the webcam
#cap = cv2.VideoCapture('video.avi')
## vs = cv2.VideoCapture(args["video"])

# Init frame variables
first_frame = None
next_frame = None

# Init display font and timeout counters
font = cv2.FONT_HERSHEY_SIMPLEX
delay_counter = 0
movement_persistent_counter = 0

##Yusufhan Kircova Additions
previously_moving = False
motion_Event_List = []
motion_Event = []

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
size = (frame_width, frame_height)

# Below VideoWriter object will create
# a frame of above defined The output 
# is stored in 'filename.avi' file.

result = cv2.VideoWriter('filename.avi', cv2.VideoWriter_fourcc(*COMPRESSION), 10, size)

# LOOP!
while True:
    
    # Set transient motion detected as false
    transient_movement_flag = False
    
    # Read frame
    ret, frame = cap.read()
    text = "Unoccupied"
    
    # Interrupt trigger by pressing q to quit the open CV program, write to data frame and check if frame is empty or not
    ch = cv2.waitKey(1)
    if frame is None or ch & 0xFF == ord('q'):
        print(motion_Event_List)
        columns = ['Sleep State Start', 'Sleep State Ended ']
        df = pd.DataFrame(motion_Event_List, columns = columns)
        df.to_excel('output1.xlsx')
        break
    
    # If there's an error in capturing
    if not ret:
        print("CAPTURE ERROR")
        continue

        
    result.write(frame)
    # Resize and save a greyscale version of the image
    frame = imutils.resize(frame, width = WIDTH, height=HEIGHT)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur it to remove camera noise (reducing false positives)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # If the first frame is nothing, initialise it
    if first_frame is None: first_frame = gray    

    delay_counter += 1

    # Otherwise, set the first frame to compare as the previous frame
    # But only if the counter reaches the appriopriate value
    # The delay is to allow relatively slow motions to be counted as large
    # motions if they're spread out far enough
    if delay_counter > FRAMES_TO_PERSIST:
        delay_counter = 0
        first_frame = next_frame

        
    # Set the next frame to compare (the current frame)
    next_frame = gray

    # Compare the two frames, find the difference
    frame_delta = cv2.absdiff(first_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # Fill in holes via dilate(), and find contours of the thesholds
    thresh = cv2.dilate(thresh, None, iterations = 2)
    (cnts, b) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:

        # Save the coordinates of all found contours
        (x, y, w, h) = cv2.boundingRect(c)
        
        # If the contour is too small, ignore it, otherwise, there's transient
        # movement
        if cv2.contourArea(c) > MIN_SIZE_FOR_MOVEMENT:
            if previously_moving == False:
                #starttime = datetime.now()
                #print("Motion Started", starttime.strftime('%Y-%m-%d %H:%M:%S'))
                #motion_Event.append(starttime.strftime('%Y-%m-%d %H:%M:%S'))
                endtime = datetime.now()
                print("No Motion State Ended - Fly Awake", endtime.strftime('%Y-%m-%d %H:%M:%S'), "\n")

                motion_Event.append(endtime.strftime('%Y-%m-%d %H:%M:%S'))
                motion_Event_List.append(motion_Event)
                motion_Event = []
                
                previously_moving = True
                
            transient_movement_flag = True
            # Draw a rectangle around big enough movements
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # The moment something moves momentarily, reset the persistent
    # movement timer.
    if transient_movement_flag == True:
        movement_persistent_flag = True
        movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE

    # As long as there was a recent transient movement, say a movement
    # was detected    
    if movement_persistent_counter > 1:           
        text = "Movement Detected " + str(movement_persistent_counter)
        movement_persistent_counter -= 1
    elif movement_persistent_counter == 1:
        starttime = datetime.now()
        print("No Motion State Started -  Fly Asleep", starttime.strftime('%Y-%m-%d %H:%M:%S'))
        motion_Event.append(starttime.strftime('%Y-%m-%d %H:%M:%S'))
        
        #endtime = datetime.now()
        #print("Motion Ended", endtime.strftime('%Y-%m-%d %H:%M:%S'), "\n")
        #motion_Event.append(endtime.strftime('%Y-%m-%d %H:%M:%S'))
        #motion_Event_List.append(motion_Event)
        #motion_Event = []
        
        movement_persistent_counter -= 1
        previously_moving = False
    else:
        text = "No Movement Detected"

    # Print the text on the screen, and display the raw and processed video 
    # feeds
    cv2.putText(frame, str(text), (10,35), font, 0.75, (255,255,255), 2, cv2.LINE_AA)
    
    # For if you want to show the individual video frames
#    cv2.imshow("frame", frame)
#    cv2.imshow("delta", frame_delta)
    
    # Convert the frame_delta to color for splicing
    frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR)

    # Splice the two video frames together to make one long horizontal one
    cv2.imshow("frame", np.hstack((frame_delta, frame)))

# Cleanup when closed
cv2.waitKey(0)
cv2.destroyAllWindows()
cap.release()
result.release()
