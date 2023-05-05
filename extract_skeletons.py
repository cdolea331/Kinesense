import cv2
import mediapipe as mp
import time
import os
import sys
import math

amateur_video = sys.argv[1]
expert_video = sys.argv[2]
target_videos = ["regular.mp4"]
target_landmarks = [0,11,12,13,14,15,16,23,24,25,26,27,28]
landmark_names = ["nose", "right shoulder", "left shoulder", "right elbow", "left elbow",
"right wrist", "left wrist", "right hip", "left hip", "right knee", "left knee", 
"right ankle", "left ankle"]
skeleton_file = "output_skeleton.csv"
output = open(skeleton_file, 'w')
title_line = "frame number,"
for x in range(13):
    name = landmark_names[x]
    title_line += "{}_x, {}_y, {}_z, {}_visibility,".format(name,name,name,name)
title_line = title_line[:-1]
title_line += "\n"
output.write(title_line)
frame_num = 0

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

class landmark_wrapper:
    def __init__(self, landmarks):
        self.landmark = landmarks


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic

# For static images:
with mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    min_detection_confidence=0.5) as pose:
    image = cv2.imread('4.jpg')  #Insert your Image Here
    image_height, image_width, _  = image.shape
    # Convert the BGR image to RGB before processing.
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # Draw pose landmarks on the image.
    annotated_image = image.copy()
    mp_drawing.draw_landmarks(annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imwrite(r'4.png', annotated_image)

# For webcam input:
#cap = cv2.VideoCapture(0)


video_landmarks = []

for video in target_videos:
    cap = cv2.VideoCapture(video)
    #For Video input:
    prevTime = 0
    j = 0
    k = 0

    frame_landmarks = []

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        model_complexity=2,
        min_tracking_confidence=0.5) as pose:
      while cap.isOpened():
        success, image = cap.read()
        if not success:
          print("Ignoring empty camera frame.")
          # If loading a video, use 'break' instead of 'continue'.
          break

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = pose.process(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        new_set = set([(11,13),(13,15), (11,12),(12,14), (12,24), (11,23), (14,16),(24,26),(23,25), (26,28), (25,27)])
        k += 1
        j += 1 if k % 4 == 0 else 0

        edited_landmarks = []
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            if i in target_landmarks:
                edited_landmarks.append(landmark)
                last_landmark = landmark
            else:
                edited_landmarks.append(last_landmark)
        skeleton_landmarks = []
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            if i in target_landmarks:
                skeleton_landmarks.append(landmark)
            else:
                pass
        # print(edited_landmarks)
        edited_landmark_wrapper = landmark_wrapper(edited_landmarks)
        frame_landmarks.append(edited_landmark_wrapper)
        mp_drawing.draw_landmarks(
            image, edited_landmark_wrapper, new_set)#mp_pose.POSE_CONNECTIONS
        new_set_iterator = iter(new_set)
        set0 = next(new_set_iterator)
        landmarks = [x for _,x in enumerate(results.pose_landmarks.landmark)]
        shoulder = (landmarks[11].x, landmarks[11].y)
        elbow = (landmarks[13].x, landmarks[13].y)
        wrist = (landmarks[15].x, landmarks[15].y)
        angle = getAngle(shoulder,elbow,wrist)
        angle = abs(angle - 360)
        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime
        cv2.putText(image, f'Arm angle: {int(angle)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 2)
        cv2.imshow('BlazePose', image)
        frame_string = "{},".format(frame_num)
        print(len(skeleton_landmarks))
        for landmark in skeleton_landmarks:
            frame_string += "{},{},{},{},".format( landmark.x, landmark.y, landmark.z, landmark.visibility)
        frame_string += "\n"

        output.write(frame_string)
        frame_num += 1
        video_landmarks.append(frame_landmarks)
        if cv2.waitKey(5) & 0xFF == 27:
          break

    cap.release()


i = 0

output.close()

    