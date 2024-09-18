import sys
import cv2
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QSlider
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import pyqtSignal
class VideoAnnotator(QMainWindow):
    closed = pyqtSignal()  # Signal to be emitted when the window is closed
    def __init__(self, video_path, bbox_file_path):
        super().__init__()
        self.cap = cv2.VideoCapture(video_path)
        self.bbox_file_path = bbox_file_path
        self.current_frame = 0
        self.rotate_amount = 0
        self.selected_bboxes = []  # To store clicked bounding boxes
        self.is_paused = True  # Initially, the video is paused

        # Get total number of frames in the video
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Get original video dimensions
        self.original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.bboxes = self.load_bboxes(bbox_file_path)
        # Calculate resize ratio to fit video to screen
        self.resize_ratio = self.calculate_resize_ratio()

        # Set up the UI
        self.setWindowTitle("Video Annotator")
        self.video_label = QLabel(self)  # QLabel to display the video frames
        self.video_label.mousePressEvent = self.select_bbox  # Mouse click handler
        self.pause_button = QPushButton("Play", self)  # Button to pause/play the video
        self.pause_button.clicked.connect(self.toggle_pause)

        # Slider for scrubbing through the video
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, self.total_frames - 1)
        self.position_slider.sliderReleased.connect(self.slider_scrub)
        self.position_slider.sliderPressed.connect(self.toggle_pause)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.position_slider)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer to handle frame updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)

    def load_bboxes(self, bbox_file_path):
        with open(bbox_file_path, 'rb') as f:
            temp = json.load(f)
            self.rotate_amount = temp.get("rotate_amount", 0)
            if abs(self.total_frames - len(temp.get("boxes", []))) > 10:
                raise ValueError("Number of frames in video and bounding boxes do not match")
            return temp.get("boxes", [])

    def save_bboxes(self):
        dump_boxes_with_rotate = {
            "boxes": self.bboxes,
            "rotate_amount": self.rotate_amount
        }
        with open(self.bbox_file_path, 'w') as file:
            json.dump(dump_boxes_with_rotate, file, indent=4)

    def calculate_resize_ratio(self):
        screen_width, screen_height = 800, 600  # Example dimensions
        width_ratio = screen_width / self.original_width
        height_ratio = screen_height / self.original_height
        return min(width_ratio, height_ratio)

    def resize_frame(self, frame):
        new_width = int(self.original_width * self.resize_ratio)
        new_height = int(self.original_height * self.resize_ratio)
        return cv2.resize(frame, (new_width, new_height))

    def display_frame(self):
        if not self.is_paused:
            # Automatically update the slider position
            self.current_frame += 1
            if self.current_frame >= self.total_frames:
                self.current_frame = self.total_frames - 1
                self.toggle_pause()  # Pause at the end of the video
            self.position_slider.setValue(self.current_frame)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()

        if not ret:
            print("End of video")
            return

        # Resize frame to fit the screen
        frame = self.resize_frame(frame)

        # Draw bounding boxes on the resized frame
        for bbox_dict in self.bboxes[self.current_frame]:
            x, y, w, h =  bbox_dict["box"]
            y, w, h = int(y * self.resize_ratio), int( w* self.resize_ratio), int( h* self.resize_ratio)
            x = int(self.resize_ratio * ((x - self.rotate_amount) % self.original_width))
            bbox_id = bbox_dict["id"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, str(bbox_id), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Convert the frame to displayable image in PyQt
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.video_label.setPixmap(pixmap)

    def select_bbox(self, event):
        # Adjust mouse click position according to resize ratio
        x_click = int(event.position().x() / self.resize_ratio)
        y_click = int(event.position().y() / self.resize_ratio)

        # Detect which bounding box was clicked
        for i, bbox_dict in enumerate(self.bboxes[self.current_frame]):
            x, y, w, h = bbox_dict["box"]
            x += self.rotate_amount  # Account for any rotation
            if x <= x_click <= x + w and y <= y_click <= y + h:
                self.selected_bboxes.append((self.current_frame, i))  # Store the clicked bounding box

        if len(self.selected_bboxes) == 2:
            self.swap_ids()

    def swap_ids(self):
        # Swap IDs of the selected bounding boxes for all frames
        frame1, index1 = self.selected_bboxes[0]
        frame2, index2 = self.selected_bboxes[1]

        id1 = self.bboxes[frame1][index1]["id"]
        id2 = self.bboxes[frame2][index2]["id"]

        # Swap the IDs in all frames where the IDs are present
        for frame in range(len(self.bboxes)):
            for bbox_dict in self.bboxes[frame]:
                if bbox_dict["id"] == id1:
                    bbox_dict["id"] = id2
                elif bbox_dict["id"] == id2:
                    bbox_dict["id"] = id1

        # Clear selection after swap
        self.selected_bboxes = []

        # Redraw the frame with updated bounding boxes
        self.display_frame()

    def slider_scrub(self):
        # Get the frame position from the slider
        self.current_frame = self.position_slider.value()
        self.display_frame()  # Display the new frame when scrubbing

    def toggle_pause(self):
        if self.is_paused:
            self.pause_button.setText("Pause")
            self.is_paused = False
            self.timer.start(30)  # Adjust interval for real-time playback (approx. 30 fps)
        else:
            self.pause_button.setText("Play")
            self.is_paused = True
            self.timer.stop()
            
    def closeEvent(self, event):
        # Save bounding boxes before closing
        self.save_bboxes()
        # Emit the custom closed signal to notify other parts of the application
        self.closed.emit()
        # Accept the close event to proceed with closing
        event.accept()

        
    def run(self):
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_path = "360_video_2m.mp4"  # Replace with your video path
    bbox_file_path = "bounding_boxes_.json"  # Replace with your bounding boxes JSON file path
    annotator = VideoAnnotator(video_path, bbox_file_path)
    annotator.run()
    sys.exit(app.exec())
