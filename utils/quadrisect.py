import cv2
import numpy as np
import argparse
import os

def quadrantize(vid) :

    cap = cv2.VideoCapture(vid)

    #get video dimensions
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    #substring of vid from last / to .mp4
    vid = vid.split('/')[-1]
    vid = vid.split('.')[0]

    if (not os.path.exists('./quadrisected_videos/' + vid)):
        os.makedirs('./quadrisected_videos/' + vid)

    output1 = cv2.VideoWriter('./quadrisected_videos/' + vid + '/1.mp4' , cv2.VideoWriter_fourcc(*'mp4v'), 30, (width // 4, height))
    output2 = cv2.VideoWriter('./quadrisected_videos/' + vid + '/2.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (width // 4, height))
    output3 = cv2.VideoWriter('./quadrisected_videos/' + vid + '/3.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (width // 4, height))
    output4 = cv2.VideoWriter('./quadrisected_videos/' + vid + '/4.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (width // 4, height))


    if (cap.isOpened()== False):
        print("Error opening video stream or file")
        exit()

    while True: 
        ret, frame = cap.read()
        if not ret:
            break

        percentDone = (cap.get(cv2.CAP_PROP_POS_FRAMES) / cap.get(cv2.CAP_PROP_FRAME_COUNT)) * 100
        print(str(percentDone) + "% done")

        crop1 = frame[:, :width // 4]
        crop2 = frame[:, width // 4:width // 2]
        crop3 = frame[:, width // 2:width // 4 * 3]
        crop4 = frame[:, width // 4 * 3:]

        output1.write(crop1)
        output2.write(crop2)
        output3.write(crop3)
        output4.write(crop4)

    cap.release()
    output1.release()
    output2.release()
    output3.release()
    output4.release()



if __name__ == "__main__" :

    args = argparse.ArgumentParser()
    args.add_argument("--video", type=str, help="Path to video file")

    args = args.parse_args()

    if not args.video:
        print("No video file provided")
        exit()

    quadrantize(args.video)

    print("Quadrisected videos saved to ./quadrisected_videos/{video_name}")

