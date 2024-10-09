# GazeXR - README

## Non-Technical Overview:
GazeXR is a tool designed to process videos of people and gaze data from a CSV file. It identifies individuals in the video, tracks them, and maps their gaze points onto the video. The tool outputs an annotated video, a CSV file, and a JSON file that stores the bounding box information for reuse.

### Typical Use Case:
1. **Input**:
   - A video file containing people.
   - A CSV file containing gaze data with columns for time, x coordinate, and y coordinate.

2. **Output**:
   - Annotated video with bounding boxes for individuals.
   - CSV file of the processed gaze data.
   - JSON file for storing bounding boxes, which can be reused for different gaze data files.

3. **Running the Tool**:
   You can run the script directly using the following command:  
   ```bash 
   python run_batch.py "path_to_video" "path_to_csv"  
   ```
   This will generate an annotated video, CSV, and JSON file for each input video-CSV pair.

4. **Fixing Errors**:
   Due to challenges in tracking people across frames, the bounding boxes might switch IDs or drift. Use the GUI utility or swapBoundingBoxes.py for manual corrections.

## Technical Overview:
The core of GazeXR relies on **YOLOv8** for detecting people in each frame. Once detected, the bounding boxes are processed using a **re-identification (reID) algorithm** to maintain consistency across frames, even in scenarios with occlusions or people leaving and re-entering the frame.

### Key Points:
1. **YOLOv8 Detection**:
   - The model uses YOLOv8’s pre-trained weights (yolov8x.pt) and only detects people (class 0 in YOLO).
   - Bounding box confidence can be adjusted in the run_detection function (conf=0.5 by default).

2. **Re-Identification**:
   - Tracks bounding boxes across frames based on overlap and proximity.
   - Boxes that do not overlap are assigned to the closest one within a 400-pixel range.
   - Parameters like overlap percentage and pixel distance can be adjusted for fine-tuning.

3. **Edge Case Handling**:
   - Detects and resolves issues with people crossing the video boundaries.
   - Gaze data is mapped to the bounding boxes based on overlap and time synchronization.

4. **Additional Fine-Tuning**:
   - If you see a high number of false positives, consider increasing the confidence threshold in the detection phase.
   - For complex scenarios, retraining YOLO on a dataset of similar contexts is recommended.

## Usage Example:
Here’s a typical usage scenario for GazeXR, along with some key functions.

### Running Detection:
```python
from ultralytics import YOLO
import torch
import cv2

def run_detection(video, conf=0.5, iou=0.4):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO("yolov8x.pt").to(device) 
    results = model.predict(source=video, conf=conf, iou=iou, classes=[0], stream=True)  
    return results  
```
### Rotating the Video for Better Detection:
The edge areas in the video can sometimes cause tracking issues. To mitigate this, you can rotate the video so that the largest gap between people is aligned with the video edges.

```python  
import numpy as np  

def rotate_image(image, rotate_amount):  
    return np.roll(image, rotate_amount, axis=1)  
```
### Graph Class for Plotting Gaze Points:
The following class is used to plot and save gaze data points over time.

```python  
import matplotlib.pyplot as plt  

class Graph:  
    def __init__(self):  
        self.fig, self.ax = plt.subplots()  
        self.data = []  

    def update(self, time, boxID):  
        self.data.append((time, boxID))  

    def sort_and_plot(self):  
        self.data.sort(key=lambda x: int(x[1]))  
        self.ax.clear()  
        times, boxIDs = zip(*self.data)  
        self.ax.scatter(times, boxIDs, marker='o', c='C0', label='Gaze Points')  
        self.fig.canvas.draw()  

    def save(self, path='gaze_points.png'):  
        self.fig.savefig(path)  
```
### Filtering Gaze Points:
This function filters gaze points based on the frame number.

```python  
import numpy as np  

def filter_list(gazeData, frame):  
    array_of_lists = np.array(gazeData)  
    filtered_list = array_of_lists[array_of_lists[:,1] == str(frame)]  
    return filtered_list  
```
### Drawing Bounding Boxes:
Draw bounding boxes around detected people in a video frame.

```python  
import cv2  

def draw_box(frame, box, thickness=3, color=(0,255,0)):  
    x, y, w, h = box["box"]  
    cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), color, thickness)  
    cv2.putText(frame, str(box["id"]), (int(x), int(y-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)  
```
### Merging Overlapping Intervals:
Merges overlapping intervals of time to prevent duplicate video segments.

```python  
def merge_intervals(intervals):  
    if not intervals:  
        return []  
    intervals.sort(key=lambda x: x[0])  
    merged = [intervals[0]]  
    for current in intervals[1:]:  
        last = merged[-1]  
        if current[0] <= last[1]:  
            merged[-1] = (last[0], max(last[1], current[1]))  
        else:  
            merged.append(current)  
    return merged  
```
### Generating a Compilation Video from Frames:
Create a video compilation based on specific frames with a given ID.

```python  
from moviepy.video.io.VideoFileClip import VideoFileClip  
from moviepy.editor import concatenate_videoclips  

def generate_compilation_from_frames(video_path, id_times, id_to_extract, leniency=0.5):  
    filtered_times = [time for time, ID in id_times if str(ID) == str(id_to_extract)]  
    intervals = [(max(0, time - leniency), time + leniency) for time in filtered_times]  
    merged_intervals = merge_intervals(intervals)  

    video = VideoFileClip(video_path)  
    clips = [video.subclip(start_time, end_time) for start_time, end_time in merged_intervals]  
    final_clip = concatenate_videoclips(clips)  

    output_path = f"{video_path.rsplit('.', 1)[0]}_{id_to_extract}.mp4"  
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")  
    return output_path  
```
### Saving Plotted Gaze Data:
Create and save a plot of gaze data points.

```python  
def generate_graph(plot, path='gaze_points.png'):  
    plot.sort_and_plot()  
    plot.save(path)  
    return path  
```
### Loading and Drawing from a JSON File:
Load the bounding boxes from a JSON file and draw them on a video.

```python  
import json  
import cv2  

def draw_boxes_from_json(json_path, video_path):  
    with open(json_path, 'rb') as file:  
        boxes_for_gaze = json.load(file)  
    cap = cv2.VideoCapture(video_path)  
    fps = int(cap.get(cv2.CAP_PROP_FPS))  
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  
    out = cv2.VideoWriter(f"{os.path.splitext(video_path)[0]}_annotated.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))  
    
    for frame_boxes in boxes_for_gaze.get("boxes", []):  
        ret, frame = cap.read()  
        if not ret:  
            break  
        for box in frame_boxes:  
            draw_box(frame, box)  
        out.write(frame)  
    
    cap.release()  
    out.release()  
```


