import math
from utils.scaleCoordinates import scale_coords
from ultralytics import YOLO
import numpy as np
import matplotlib.pyplot as plt
from utils.csvReader import read as csvRead
import cv2
import os
import json
import shutil
import copy
import ffmpeg
import csv
import itertools
import torch

# Load model and run inference on the video
def run_detection(video, progress=None):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = YOLO("yolov9e.pt").to(device)
    cap = cv2.VideoCapture(video)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)  # Keep FPS as float for more accurate timing
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Extract the first frame
    ret, first_frame = cap.read()

    if not ret:
        print("Failed to read the video.")
        cap.release()
        return None, None

    # Make a prediction on the first frame
    results_first_frame = model(first_frame, classes=[0], conf=0.225, iou=0.4)
    boxes_first_frame = results_first_frame[0].boxes

    # Extract edges of the bounding boxes
    box_edges = [(box.xywh[0][0].item() - box.xywh[0][2].item() / 2, 
                  box.xywh[0][0].item() + box.xywh[0][2].item() / 2) for box in boxes_first_frame]

    # Sort by the left edge of the boxes
    box_edges = sorted(box_edges, key=lambda x: x[0])

    # Calculate gaps between the right edge of one box and the left edge of the next box
    gaps = [(box_edges[i+1][0] - box_edges[i][1], i) for i in range(len(box_edges)-1)]

    # Add gaps between the last box and the first box for wrap-around calculation
    wrap_around_gap = (frame_width - box_edges[-1][1] + box_edges[0][0], len(box_edges)-1)
    gaps.append(wrap_around_gap)

    # Sort gaps in descending order
    gaps.sort(reverse=True, key=lambda x: x[0])

    # Determine the rotation amount to center the largest gap
    largest_gap_index = gaps[0][1]

    # Calculate center of largest gap
    if largest_gap_index == len(box_edges) - 1:
        # Gap between last and first box (wrap-around)
        gap_center = (box_edges[0][0] + frame_width + box_edges[-1][1]) / 2
        if gap_center > frame_width:
            gap_center -= frame_width
    else:
        # Regular gap
        gap_center = (box_edges[largest_gap_index][1] + box_edges[largest_gap_index + 1][0]) / 2

    # Calculate rotation amount to bring gap center to frame center
    rotate_amount = int(frame_width / 2 - gap_center)
    rotate_amount = rotate_amount + frame_width // 2

    # Create a function to rotate the image horizontally (wrap around)
    def rotate_image(image, rotate_amount):
        return np.roll(image, rotate_amount, axis=1)

    # Rotate the first frame
    rotated_frame = rotate_image(first_frame, rotate_amount)

    # Create a folder for saving rotated video
    output_folder = f"rotated_{video.split('/')[-1].split('.')[0]}"
    counter = 1
    unique_output_folder = output_folder  # Store the base folder name

    while os.path.exists(unique_output_folder):
        unique_output_folder = f"{output_folder}({counter})"
        counter += 1

    # Create the unique directory
    os.makedirs(unique_output_folder, exist_ok=True)
    output_path = os.path.join(unique_output_folder, 'rotated_video.mp4')

    # Save the rotated frames to the video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' codec for mp4 files
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    out.write(rotated_frame)

    # Process the rest of the video with YOLO after rotating
    for i in range(1, num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        rotated_frame = rotate_image(frame, rotate_amount)
        
        progress_percentage = int((i + 1) / (num_frames * 2) * 70)  # *2 because rotation + detection
        progress.emit(progress_percentage)
        
        out.write(rotated_frame)

    cap.release()
    out.release()

    # Verify that the video file was properly created and finalized
    if not os.path.exists(output_path):
        print(f"Error: Failed to create output video file at {output_path}")
        return None, None

    # Re-run detection on the rotated video
    if progress is not None:
        results = []
        frames_processed = 0
        for result in model(source=output_path, stream=True, exist_ok=True, classes=[0], conf=0.5, iou=0.4, device=device):
            results.append(result.boxes)
            frames_processed += 1

            # Update progress during YOLO detection
            progress_percentage = int(((num_frames + frames_processed) / (num_frames * 2)) * 70)  # Second phase progress
            progress.emit(progress_percentage)
    else: 
        results = model(source=output_path, stream=True, exist_ok=True, classes=[0], conf=0.5, iou=0.4, device=device)
        results = [result.boxes for result in results]
    return output_path, results, rotate_amount

plt.switch_backend('Agg')

class GazePoint:

    def get_frame_data(self):
        array_of_lists = np.array(self.gazeData)
        filtered_list = array_of_lists[array_of_lists[:,1] == str(self.frame)]
        filtered_list.tolist()
        filtered_list = [tuple(x) for x in filtered_list]
        filtered_list = list(set(filtered_list))

        return filtered_list

    def __init__(self, gazeData, frame):
        self.frame = frame
        self.gazeData = gazeData
        self.gazePoints = self.get_frame_data()
        self.x = []
        self.y = []
        for point in self.gazePoints:
            self.x.append(point[2])
            self.y.append(point[3])

        self.time = float(frame/30)


#Graph class for plotting gaze points over time
class Graph:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.data = []  # List to store the data points (time, boxID)
        
    def update(self, time, boxID):
        # Store the data points
        self.data.append((time, boxID))

    def sort_and_plot(self):
        # Sort the data by boxID
        self.data.sort(key=lambda x: int(x[1]))

        # Clear the current plot
        self.ax.clear()

        # Re-plot all data points in sorted order
        color = 'C0'  # Color for all points
        times, boxIDs = zip(*self.data)  # Unzip the sorted data into times and boxIDs
        self.ax.scatter(times, boxIDs, marker='o', c=color, label='Gaze Points')
        
        # Redraw the plot to update it
        self.fig.canvas.draw()
    def dump_to_csv(self, filename='gaze_points'):
        # Check if the file already exists, if so, append an ID
        base_filename, file_extension = os.path.splitext(filename)
        counter = itertools.count(1)
        
        # Keep adding an ID until we find a filename that doesn't exist
        while os.path.exists(filename):
            filename = f"{base_filename}_{next(counter)}{file_extension}"
        
        # Open the file in write mode
        with open(f"{filename}.csv", mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)
            
            # Optionally write the header
            writer.writerow(["Time", "BoxID"])
            
            # Write the data rows
            writer.writerows(self.data)
        
    def save(self, path='gaze_points.png'):
        self.fig.canvas.draw() 
        plt.pause(0.01)
        self.fig.savefig(path)
        return path
        


def filter_list(gazeData, frame):
    array_of_lists = np.array(gazeData)
    filtered_list = array_of_lists[array_of_lists[:,1] == str(frame)]
    filtered_list.tolist()
    return filtered_list



def intersect(gazePoint, boundingBoxes, graph, rotate_amount):

    #iterate through all bounding boxes for this frame
    for box in boundingBoxes:
        #get bounding box coordinates
        x1 = box["box"][0] 
        y1 = box["box"][1]
        x2 = x1 + box["box"][2]
        y2 = y1 + box["box"][3]


        #convert to floats
        x1 = float(x1)
        x2 = float(x2)
        y1 = float(y1)
        y2 = float(y2)

        #iterate through all gaze point for this frame
        for x, y in zip(gazePoint.x, gazePoint.y):
            x, y = scale_coords(x, y, (3840, 1920), (5760, 2880))
            x = (x + rotate_amount) % 3840
            #check if gaze point is within bounding box
            if x1 < x and x < x2 and y1 < y and y < y2:
                    graph.update(gazePoint.time, str(box["id"]))
                    
                    
def calculate_overlap(box1, box2, screen_width, overlap_margin=50, percentage=None):
    """
    Calculate the overlapping area between two boxes, considering horizontal screen wrap-around.

    Parameters:
    box1, box2: Dict with "box" as Tuple of (x, y, w, h)
        x, y: Coordinates of the top-left corner of the box.
        w, h: Width and height of the box.
    screen_width: int
        The width of the screen.
    overlap_margin: int
        The margin of overlap to consider at the screen edges.
    percentage: float, optional
        The minimum percentage of overlap required to consider as valid.

    Returns:
    overlap_area: float
        The area of overlap between the two boxes, or -1 if no valid overlap.
    """
    # Unpack the boxes
    x1, y1, w1, h1 = box1["box"]
    x2, y2, w2, h2 = box2["box"]

    # Calculate the standard intersection
    def get_overlap_area(x1, y1, w1, h1, x2, y2, w2, h2):
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0  # No overlap
        
        overlap_width = x_right - x_left
        overlap_height = y_bottom - y_top
        return overlap_width * overlap_height

    # Standard overlap area
    overlap_area = get_overlap_area(x1, y1, w1, h1, x2, y2, w2, h2)

    # Check for overlap across screen edges (horizontal)
    if x1 < overlap_margin:
        # Overlapping on the left side, check the right side wrap-around
        overlap_area = max(overlap_area, get_overlap_area(x1 + screen_width, y1, w1, h1, x2, y2, w2, h2))
    elif x1 + w1 > screen_width - overlap_margin:
        # Overlapping on the right side, check the left side wrap-around
        overlap_area = max(overlap_area, get_overlap_area(x1 - screen_width, y1, w1, h1, x2, y2, w2, h2))

    if overlap_area == 0:
        return -1

    # Ensure the overlap is greater than the largest overlap tracked
    if box2["largestOverlap"] > overlap_area:
        return -1

    # Calculate areas for percentage-based check
    area1 = w1 * h1
    area2 = w2 * h2

    decay_factor = 0.6
    if percentage is not None:
        decay_factor = percentage

    # Check if the overlap area is less than the decay factor of either box's area
    if overlap_area < decay_factor * area1 and overlap_area < decay_factor * area2:
        return -1  # Overlap is less than the required percentage
    
    subtract_decay = 0
    
    if box1["decay"] > 3:
        subtract_decay = 700 * box1["decay"]
    return overlap_area - subtract_decay



def draw_box(frame, box, thickness=3, color=(0,255,0)):
    x, y, w, h = box["box"]
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    cv2.rectangle(frame, (x,y), (x+w, y+h), color, thickness)
    cv2.putText(frame, str(box["id"]), (x, y-10),  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    
    
def convert_to_xywh(bbox_array):
    """
    Convert bounding box array from (x_min, y_min, x_max, y_max) to (x, y, w, h).
    
    Parameters:
    bbox_array (numpy.ndarray): Array containing bounding box coordinates and other data.
    
    Returns:
    list: A list containing [x, y, w, h] coordinates.
    """
    x_min, y_min, x_max, y_max = bbox_array[:4]
    x = x_min
    y = y_min
    w = x_max - x_min
    h = y_max - y_min
    return [x, y, w, h]



def calculate_wrapped_distance(box1, box2, screen_width):
    """
    Calculate the wrapped Euclidean distance between two boxes, allowing for wrap-around at screen edges.

    Parameters:
    box1, box2: dict
        Dictionaries containing bounding box information, including center coordinates.
    screen_width: int
        The width of the screen (in pixels) to handle wrap-around calculations.

    Returns:
    float
        The Euclidean distance between the centers of the two boxes, accounting for screen wrap-around.
    """
    # Calculate Euclidean distance with screen wrapping in mind
    center1_x, center1_y = box1["box"][0], box1["box"][1]
    center2_x, center2_y = box2["box"][0], box2["box"][1]
    
    dx = abs(center1_x - center2_x)
    dy = abs(center1_y - center2_y)
    
    # If the distance along the x-axis is greater than half the screen width, wrap around
    if dx > screen_width / 2:
        dx = screen_width - dx
    
    return np.sqrt(dx**2 + dy**2)

def check_for_box_jumping_to_edges(box, box2, frame_left_margin, frame_right_margin, frame_width):
    if box["box"][0] < frame_left_margin and box2["box"][0] < frame_width / 2:
        return False
    if box["box"][0] > frame_right_margin and box2["box"][0] > frame_width / 2:
        return False
    return True



def reID(input_path, results, rotate_amount, progress):
    box_with_ID = {
        "box": [],
        "id": -1,
        "decay": 0,
        "largestOverlap": 0
    }
    list_of_frames = []
    num_of_people = 0
    for result in results:
        list_of_boxes_with_ID = []
        for box in result:
            box_with_ID["box"] = convert_to_xywh(box.data.cpu().numpy()[0])
            list_of_boxes_with_ID.append(copy.deepcopy(box_with_ID))
            box_with_ID = {
                "box": [],
                "id": -1,
                "decay": 0,
                "largestOverlap": 0
            }
        list_of_frames.append(list_of_boxes_with_ID)
        
        if len(list_of_boxes_with_ID) > num_of_people:
            num_of_people = len(list_of_boxes_with_ID)
            longest_list_of_boxes_with_ID = list_of_boxes_with_ID
    unique_output_folder = os.path.dirname(input_path)
    folder_name = os.path.basename(unique_output_folder) 
    cap = cv2.VideoCapture(input_path)

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_left_margin = frame_width / 14
    frame_right_margin = frame_width * 13 / 14
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total frames for progress tracking

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'XVID' can also be used for .avi files
    out = cv2.VideoWriter(f"results_{folder_name}.mp4", fourcc, fps, (frame_width, frame_height))

    id_for_box = 0
    current_boxes = []
    boxes_for_gaze = []

    for box in list_of_frames[1]:
        box["id"] = id_for_box
        current_boxes.append(copy.deepcopy(box))
        id_for_box += 1

    # Progress initialization: we will emit updates from 70% to 100%
    initial_progress = 70
    progress_range = 30
    frames_processed = 0

    while cap.isOpened():
        for i, frame in enumerate(list_of_frames):
            if i == len(list_of_frames) - 1:
                break

            # Read the frame from the video
            ret, frames_cv2 = cap.read()
            if not ret:
                break

            # Update progress during each frame processing
            frames_processed += 1
            progress_percentage = initial_progress + int((frames_processed / num_frames) * progress_range)
            progress.emit(progress_percentage)

            for k, box in enumerate(current_boxes):
                box["decay"] += 1
                max_overlap = -1
                index = 0
                for j, box2 in enumerate(frame):
                    if box["box"][0] < frame_left_margin or (box["box"][0]) > frame_width * 13 / 14:
                        continue
                    overlap = calculate_overlap(box, box2, frame_width)
                    if overlap > max_overlap:
                        max_overlap = overlap
                        index = j
                        list_of_frames[i][j]["id"] = box["id"]
                        list_of_frames[i][j]["largestOverlap"] = max_overlap
                        list_of_frames[i][j]["decay"] = 0

            for k, box in enumerate(current_boxes):
                max_overlap = -1
                index = 0
                for j, box2 in enumerate(frame):
                    if box2["id"] == -1 and (all(box["id"] != other_box["id"] for other_box in list_of_frames[i] if other_box is not box)):
                        if box["box"][0] < frame_left_margin or (box["box"][0]) > frame_right_margin:
                            continue
                        overlap = calculate_overlap(box, box2, frame_width, percentage=0.1)
                        if overlap > max_overlap:
                            max_overlap = overlap
                            index = j
                            list_of_frames[i][j]["id"] = box["id"]
                            list_of_frames[i][j]["largestOverlap"] = max_overlap
                            list_of_frames[i][j]["decay"] = 0

            for box in frame:
                if box["id"] != -1:
                    current_boxes[box["id"]] = copy.deepcopy(box)

            for box in frame:
                if box["id"] == -1:
                    min_distance = float('inf')
                    closest_box_index = None
                    cx1, cy1 = box["box"][0] + box["box"][2] / 2, box["box"][1] + box["box"][3] / 2
                    for idx, curr_box in enumerate(current_boxes):
                        if curr_box["decay"] != 0 or curr_box["box"][0] < frame_left_margin or (curr_box["box"][0]) > frame_right_margin:
                            cx2, cy2 = curr_box["box"][0] + curr_box["box"][2] / 2, curr_box["box"][1] + curr_box["box"][3] / 2
                            dx = abs(cx2 - cx1)
                            dx = min(dx, frame_width - dx)
                            dy = abs(cy2 - cy1)
                            distance = np.sqrt(dx ** 2 + dy ** 2)
                            if curr_box["box"][0] < frame_left_margin or (curr_box["box"][0]) > frame_right_margin:
                                distance -= 100
                            if distance < min_distance:
                                min_distance = distance
                                closest_box_index = idx
                    if closest_box_index is not None and min_distance < 400 and check_for_box_jumping_to_edges(box, current_boxes[closest_box_index], frame_left_margin, frame_right_margin, frame_width):
                        box["id"] = current_boxes[closest_box_index]["id"]
                        box["largestOverlap"] = 0
                        box["decay"] = 0
                        current_boxes[closest_box_index] = copy.deepcopy(box)
                    elif box["box"][0] < frame_left_margin or (box["box"][0]) > frame_right_margin:
                        continue
                    else:
                        box["id"] = id_for_box
                        current_boxes.append(box)
                        id_for_box += 1

            current_box_frame = []
            for box in current_boxes:
                append_box = copy.deepcopy(box)
                append_box["id"] += 1
                current_box_frame.append(append_box)
                cv2.putText(frames_cv2, str(i), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                draw_box(frames_cv2, box)

            boxes_for_gaze.append(current_box_frame)
            out.write(frames_cv2)

        cap.release()
        out.release()


    dump_boxes_with_rotate = {
        "boxes": boxes_for_gaze,
        "rotate_amount": rotate_amount
    }
    dump_boxes_with_rotate = convert_to_serializable(dump_boxes_with_rotate)

    with open(f"bounding_boxes_{folder_name}.json", 'w') as file:
        json.dump(dump_boxes_with_rotate, file, indent=4)
        
    if os.path.exists(unique_output_folder):
        shutil.rmtree(unique_output_folder)
    # Return the JSON file path and the video path
    return f"bounding_boxes_{folder_name}.json", f"results_{folder_name}.mp4"


def convert_to_serializable(data):
    """Convert non-serializable objects (e.g., NumPy arrays, float32) into JSON-serializable types."""
    if isinstance(data, np.ndarray):
        return data.tolist()  # Convert NumPy array to a list
    elif isinstance(data, (np.float32, np.float64)):
        return float(data)  # Convert NumPy float to Python float
    elif isinstance(data, (np.int32, np.int64)):
        return int(data)  # Convert NumPy int to Python int
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]  # Recursively handle lists
    elif isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}  # Recursively handle dicts
    else:
        return data  # Return other types as-is (assumed to be serializable)
    
    
def merge_intervals(intervals):
    """
    Merge overlapping intervals.
    
    :param intervals: List of tuples representing intervals (start, end).
    :return: List of merged intervals.
    """
    if not intervals:
        return []
    
    # Sort intervals by the start time
    intervals.sort(key=lambda x: x[0])
    merged_intervals = [intervals[0]]

    for current in intervals[1:]:  # Start from second interval since first is already in merged_intervals
        last_merged = merged_intervals[-1]
        
        # If the current interval overlaps with the last merged one, merge them
        if current[0] <= last_merged[1]:
            merged_intervals[-1] = (last_merged[0], max(last_merged[1], current[1]))
        else:
            merged_intervals.append(current)

    return merged_intervals

def generate_compilation_from_frames(video_path, id_times, id_to_extract, leniency=0.5):
    """
    Generate a video compilation from the original video based on specific frames associated with an ID.

    :param video_path: Path to the input video file.
    :param id_times: A set of tuples with each tuple containing (time, id).
    :param output_path: Path where the output video will be saved.
    :param id_to_extract: The ID for which to extract video segments.
    :param leniency: Seconds before and after each frame to include in the clip (default is 0.5 seconds).
    """
    # Filter times for the specific ID
    filtered_times = [time for time, ID in id_times if str(ID) == str(id_to_extract)]
    
    if not filtered_times:
        print(f"No times found for ID '{id_to_extract}'. Exiting.")
        return

    # Create intervals around each frame time with leniency
    intervals = [(max(0, time - leniency), time + leniency) for time in filtered_times]
    
    # Merge overlapping intervals
    merged_intervals = merge_intervals(intervals)

    # Temporary file list to store the extracted segments
    temp_files = []

    # Extract each merged segment and save to a temporary file
    for idx, (start_time, end_time) in enumerate(merged_intervals):
        temp_file = f'temp_segment_{idx}.mp4'
        temp_files.append(temp_file)

        # Use ffmpeg to extract the segment
        (
            ffmpeg
            .input(video_path, ss=start_time, to=end_time)
            .output(temp_file, c='copy')  # 'copy' codec to avoid re-encoding
            .run(overwrite_output=True)
        )

    # Create a list file to concatenate all segments
    with open('file_list.txt', 'w') as f:
        for temp_file in temp_files:
            # Correctly format the file path
            f.write(f"file '{temp_file}'\n")

    # Debugging: print out the contents of file_list.txt
    with open('file_list.txt', 'r') as f:
        content = f.read()

    # Use ffmpeg to concatenate all segments into one video
    (
        ffmpeg
        .input('file_list.txt', format='concat', safe=0)
        .output(f"{os.path.splitext(video_path)[0]}_{id_to_extract}{os.path.splitext(video_path)[1]}", c='copy')
        .run(overwrite_output=True)
    )

    # Clean up temporary files
    for temp_file in temp_files:
        os.remove(temp_file)
    os.remove('file_list.txt')

    return f"Compilation video saved to {str(id_to_extract) + video_path}"


def initialize_plot_data(json_path, csv_path): 
        with open(json_path, 'rb') as file:
                data = json.load(file)
        boxes_for_gaze = data.get("boxes", [])
        rotate_amount = data.get("rotate_amount", 0)
        gazeData = csvRead(csv_path)
        plot = Graph() #initialize plot
        for frame, set_of_boxes in enumerate(boxes_for_gaze):
                gazePoint = GazePoint(gazeData, frame)
                intersect(gazePoint, set_of_boxes, plot, rotate_amount)
        return plot
    
    
def draw_boxes_from_pkl(json_path, video_path):
    # Load the bounding boxes from the pickle file
    with open(json_path, 'rb') as file:
        boxes_for_gaze = json.load(file)

    boxes_for_gaze = boxes_for_gaze.get("boxes", [])
    # Open the input video
    cap = cv2.VideoCapture(video_path)
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec if necessary
    # Initialize the video writer for the output video
    out = cv2.VideoWriter(f"{os.path.splitext(video_path)[0]}_annotated{os.path.splitext(video_path)[1]}", fourcc, fps, (frame_width, frame_height))
    while cap.isOpened():
        for frame_number, frame_boxes in enumerate(boxes_for_gaze):
            ret, frame = cap.read()
            if not ret:
                break

    # Draw the bounding boxes for the current frame
            for box in frame_boxes:
                draw_box(frame, box)

    # Write the processed frame to the output video
            out.write(frame)


    # Release the video capture and writer objects
    cap.release()
    out.release()
    

    
def generate_graph(plot, path='gaze_points.png'):
    plot.sort_and_plot()
    plot.dump_to_csv(path)
    plot.save(path)
    return path