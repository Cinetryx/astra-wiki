#!/usr/bin/python
import cv2
import numpy as np
from openni import openni2
from openni import _openni2 as c_api

# Initialize the depth device
openni2.initialize()
dev = openni2.Device.open_any()

# Start the depth stream
depth_stream = dev.create_depth_stream()
depth_stream.start()
depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_100_UM, resolutionX = 640, resolutionY = 480, fps = 30))

# Start the color stream
color_stream = dev.create_color_stream()
color_stream.start()
color_stream.set_video_mode(c_api.OniVideoMode(pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX = 640, resolutionY = 480, fps = 30))

# Function to return some pixel information when the OpenCV window is clicked
refPt = []
selecting = False

def point_and_shoot(event, x, y, flags, param):
    global refPt, selecting
    if event == cv2.EVENT_LBUTTONDOWN:
        print "Mouse Down"
        refPt = [(x,y)]
        selecting = True
        print refPt
    elif event == cv2.EVENT_LBUTTONUP:
        print "Mouse Up"
        refPt.append((x,y))
        selecting = False
        print refPt
        # noting the other two vertices of the rectangle and printing
        refPt.append((refPt[1][0], refPt[0][1]))
        refPt.append((refPt[0][0], refPt[1][1]))
        print "The co-ordinates of ROI: ", refPt
        roi = color_img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0], 1]
        #print roi.shape 
        print "Mean of ROI: ", roi.mean()
        print "Max of ROI: ", roi.max()
        print "Min of ROI: ", roi.min()
        print "Standard Deviation of ROI: ", np.std(roi)
        print "Length of ROI: ", len(roi)


#def stats():
# Initial OpenCV Window Functions
cv2.namedWindow("Depth Image")
cv2.setMouseCallback("Depth Image", point_and_shoot)

# Loop
while True:
    # Grab a new depth frame
    depth_frame = depth_stream.read_frame()
    depth_frame_data = depth_frame.get_buffer_as_uint16()

    # Grab a new color frame
    color_frame = color_stream.read_frame()
    color_frame_data = color_frame.get_buffer_as_uint8()

    # Put the depth frame into a numpy array and reshape it
    depth_img = np.frombuffer(depth_frame_data, dtype=np.uint16)
    depth_img.shape = (1, 480, 640)
    depth_img = np.concatenate((depth_img, depth_img, depth_img), axis=0)
    depth_img = np.swapaxes(depth_img, 0, 2)
    depth_img = np.swapaxes(depth_img, 0, 1)

    # Put the color frame into a numpy array, reshape it, and convert from bgr to rgb
    color_img = np.frombuffer(color_frame_data, dtype=np.uint8)
    color_img.shape = (480, 640, 3)
    color_img = color_img[...,::-1]

    if len(refPt) > 1:
        color_img= color_img.copy()
        cv2.rectangle(color_img, refPt[0], refPt[1], (0, 255, 0), 2)
        depth_img= depth_img.copy()
        cv2.rectangle(depth_img, refPt[0], refPt[1], (0, 255, 0), 2)
    depth_img = cv2.convertScaleAbs(depth_img, alpha=(255.0/65535.0))
    img = np.concatenate((color_img, depth_img), 1)
        
    # Display the reshaped depth frame using OpenCV
    cv2.imshow("Depth Image", img)
    key = cv2.waitKey(1) & 0xFF

    # If the 'c' key is pressed, break the while loop
    if key == ord("c"):
        break

# Close all windows and unload the depth device
depth_frame.stop()
color_frame.stop()
openni2.unload()
cv2.destroyAllWindows()