import cv2
import json

class VideoAnnotator:
    def __init__(self, video_path, bbox_file_path):
        self.cap = cv2.VideoCapture(video_path)
        self.bboxes = self.load_bboxes(bbox_file_path)
        self.bbox_file_path = bbox_file_path
        self.current_frame = 0
        self.rotate_amount = 0
        self.selected_bboxes = []
        self.playback_speed = 1  # Initial playback speed (1x)
        self.play_direction = 1  # 1 for forward, -1 for backward

        # Get original video dimensions
        self.original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate resize ratio to fit video to screen
        self.resize_ratio = self.calculate_resize_ratio()

    def load_bboxes(self, bbox_file_path):
        with open(bbox_file_path, 'rb') as f:
            
            temp = json.load(f)
            self.rotate_amount = temp.get("rotate_amount", 0)
            return temp.get("boxes", [])

    def save_bboxes(self):
        dump_boxes_with_rotate = {
        "boxes": self.bboxes,
        "rotate_amount": self.rotate_amount
    }
    # Step 3: Open a file in binary write mode
        with open(bbox_file_path, 'w') as file:
            json.dump(dump_boxes_with_rotate, file, indent=4)  # Optionally use indent for pretty-printing


    def calculate_resize_ratio(self):
        # Get the screen dimensions
        screen_width, screen_height = 800, 600  # Example dimensions; replace with actual screen size if needed
        width_ratio = screen_width / self.original_width
        height_ratio = screen_height / self.original_height
        return min(width_ratio, height_ratio)

    def resize_frame(self, frame):
        # Resize frame based on the calculated resize ratio
        new_width = int(self.original_width * self.resize_ratio)
        new_height = int(self.original_height * self.resize_ratio)
        return cv2.resize(frame, (new_width, new_height))

    def display_frame(self):
        # Adjust the frame position based on playback speed and direction
        self.current_frame += self.playback_speed * self.play_direction

        # Ensure the frame number is within valid range
        if self.current_frame >= len(self.bboxes):
            self.current_frame = len(self.bboxes) - 1
        elif self.current_frame < 0:
            self.current_frame = 0

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()

        if not ret:
            print("End of video")
            return

        # Resize frame to fit the screen
        frame = self.resize_frame(frame)

        # Draw bounding boxes on the resized frame
        for bbox_dict in self.bboxes[self.current_frame]:
            x, y, w, h = [int(coord * self.resize_ratio) for coord in bbox_dict["box"]]
            bbox_id = bbox_dict["id"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, str(bbox_id), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Display frame in a window
        cv2.imshow('Video', frame)
        cv2.setMouseCallback('Video', self.select_bbox)

    def select_bbox(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Adjust mouse click position according to resize ratio
            x = int(x / self.resize_ratio)
            y = int(y / self.resize_ratio)

            # Detect which bounding box was clicked
            for i, bbox_dict in enumerate(self.bboxes[self.current_frame]):
                x1, y1, w, h = bbox_dict["box"]
                if x1 <= x <= x1 + w and y1 <= y <= y1 + h:
                    self.selected_bboxes.append((self.current_frame, i))
                    break

            if len(self.selected_bboxes) == 2:
                self.swap_ids()

    def swap_ids(self):
        # Swap IDs of the selected bounding boxes for the rest of the frames
        frame1, index1 = self.selected_bboxes[0]
        frame2, index2 = self.selected_bboxes[1]

        id1 = self.bboxes[frame1][index1]["id"]
        id2 = self.bboxes[frame2][index2]["id"]

        # First pass: change all id1 to a temporary id
        temp_id = -2  # Use a temporary ID that is guaranteed not to be in use

        for frame in range(len(self.bboxes)):
            for bbox_dict in self.bboxes[frame]:
                if bbox_dict["id"] == id1:
                    bbox_dict["id"] = temp_id

        # Second pass: change all id2 to id1
        for frame in range(len(self.bboxes)):
            for bbox_dict in self.bboxes[frame]:
                if bbox_dict["id"] == id2:
                    bbox_dict["id"] = id1

        # Third pass: change all temp_id to id2
        for frame in range(len(self.bboxes)):
            for bbox_dict in self.bboxes[frame]:
                if bbox_dict["id"] == temp_id:
                    bbox_dict["id"] = id2

        # Clear selection
        self.selected_bboxes = []

    def run(self):
        while self.cap.isOpened():
            self.display_frame()

            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):  # Exit if 'q' is pressed
                break
            elif key == ord(' ') or key == ord("k"):  # Pause/play if spacebar or k is pressed
                if self.playback_speed != 0:
                    self.playback_speed = 0  # Pause
                else:
                    self.playback_speed = 1  # Play at normal speed
            elif key == ord('l'):  # Frame forward
                self.playback_speed = 0  # Pause the video
                self.current_frame += 1  # Move forward one frame
                if self.current_frame >= len(self.bboxes):
                    self.current_frame = len(self.bboxes) - 1
            elif key == ord('j'):  # Frame backward
                self.playback_speed = 0  # Pause the video
                self.current_frame -= 1  # Move backward one frame
                if self.current_frame < 0:
                    self.current_frame = 0
            elif key == ord('d'):
                self.playback_speed = self.playback_speed * 2 if self.playback_speed > 0 and self.play_direction == 1 else 1
                self.play_direction = 1
            elif key == ord('a'):
                self.playback_speed = self.playback_speed * 2 if self.playback_speed > 0 and self.play_direction == -1 else 1
                self.play_direction = -1
        self.save_bboxes()
        
        self.cap.release()
        cv2.destroyAllWindows()



