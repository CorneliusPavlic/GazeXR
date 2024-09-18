
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDialog,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QWaitCondition, QMutex
from GazeXR import (
    run_detection,
    reID,
    initialize_plot_data,
    generate_graph,
    generate_compilation_from_frames,
    draw_boxes_from_pkl,
)
from PyQt6.QtCore import QThread, pyqtSignal
from generateGraphFunctions import (generate_graph_popup, generate_IDs, generate_bounding_boxes, help_box)
from video_annotator import VideoAnnotator
import os
class Worker(QThread):
    progress = pyqtSignal(int)  # Signal to emit progress updates
    finished = pyqtSignal(str)  # Signal to emit when the task is complete
    error = pyqtSignal(str)  # Signal to emit errors
    show_video = pyqtSignal(str, str)
    
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task  # The task (function) to be executed
        self.args = args  # Positional arguments for the task
        self.kwargs = kwargs  # Keyword arguments for the task
        self.paused = False  # Flag to handle the pause state
        self._pause_condition = QWaitCondition()  # Condition for pausing
        self._mutex = QMutex()  # Mutex for thread safety

    def run(self):
        """Run the provided task in a separate thread."""
        try:
            result = self.task(self.progress, self.show_video, self, *self.args, **self.kwargs)
            self.finished.emit(result)   # Emit finished signal when done
        except Exception as e:
            self.error.emit(str(e))  # Emit error signal if an exception occurs

    def pause(self):
        """Pause the thread execution."""
        self._mutex.lock()
        self.paused = True
        self._mutex.unlock()

    def resume_from_video(self):
        self._mutex.lock()
        self._pause_condition.wakeAll()
        self._mutex.unlock()

    def check_pause(self):
        """Method to periodically check if the thread is paused and wait if it is."""
        self._mutex.lock()
        while self.paused:
            self._pause_condition.wait(self._mutex)
        self._mutex.unlock()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.queue = []
        self.video_path = ""
        self.gaze_path = ""
        self.json_path = ""
        self.processed_video = ""
        self.graph_path = ""
        self.button = ""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(917, 620)
        MainWindow.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        MainWindow.setStyleSheet("background-color: rgb(75, 75, 75);\n" "")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, -1, 20, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.generate_plot = QtWidgets.QPushButton(parent=self.centralwidget)
        self.generate_plot.setMaximumSize(QtCore.QSize(171, 16777215))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.WindowText, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Button, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Light, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Midlight, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Dark, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Mid, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Text, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.BrightText, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.ButtonText, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Base, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Window, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Shadow, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active,
            QtGui.QPalette.ColorRole.AlternateBase,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active,
            QtGui.QPalette.ColorRole.ToolTipBase,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active,
            QtGui.QPalette.ColorRole.ToolTipText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Active,
            QtGui.QPalette.ColorRole.PlaceholderText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive,
            QtGui.QPalette.ColorRole.WindowText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Button, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Light, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Midlight, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Dark, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Mid, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Text, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive,
            QtGui.QPalette.ColorRole.BrightText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive,
            QtGui.QPalette.ColorRole.ButtonText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Base, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Window, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.Shadow, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive,
            QtGui.QPalette.ColorRole.AlternateBase,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive,
            QtGui.QPalette.ColorRole.ToolTipBase,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive,
            QtGui.QPalette.ColorRole.ToolTipText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Inactive,
            QtGui.QPalette.ColorRole.PlaceholderText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.WindowText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Button, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Light, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Midlight, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(127, 127, 127))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Dark, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(170, 170, 170))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Mid, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.BrightText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.ButtonText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Base, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(34, 34, 34))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Window, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Shadow, brush
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.AlternateBase,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.ToolTipBase,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.ToolTipText,
            brush,
        )
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.PlaceholderText,
            brush,
        )
        self.generate_plot.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("serif")
        font.setItalic(True)
        self.generate_plot.setFont(font)
        self.generate_plot.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        )
        self.generate_plot.setStyleSheet(
            ".QPushButton {\n"
            "    font-family: serif;\n"
            "    color: #fff;\n"
            "    background-color: #222;\n"
            "    border: .1em solid #222;\n"
            "    text-transform: lowercase;\n"
            "    padding: .5em 2em;\n"
            "\n"
            "    border-radius: 5px;\n"
            "    font-style: italic;\n"
            "    transition: all .5s ease;\n"
            "    cursor: pointer;\n"
            "    font-size: 2rem;\n"
            "}\n"
            "\n"
            ".QPushButton:hover {\n"
            "    color: #222;\n"
            "    background: #fff;\n"
            "}"
        )
        self.generate_plot.setCheckable(False)
        self.generate_plot.setObjectName("generate_plot")
        self.generate_plot.clicked.connect(lambda: self.show_popup(generate_graph_popup))
        self.verticalLayout.addWidget(self.generate_plot)
        self.extract_id = QtWidgets.QPushButton(parent=self.centralwidget)
        self.extract_id.setMaximumSize(QtCore.QSize(171, 16777215))
        self.extract_id.setStyleSheet(
            ".QPushButton {\n"
            "    font-family: serif;\n"
            "    color: #fff;\n"
            "    background-color: #222;\n"
            "    border: .1em solid #222;\n"
            "    text-transform: lowercase;\n"
            "    padding: .5em 2em;\n"
            "    border-radius: 5px;\n"
            "    font-style: italic;\n"
            "    transition: all .5s ease;\n"
            "    cursor: pointer;\n"
            "    font-size: 2rem;\n"
            "}\n"
            "\n"
            ".QPushButton:hover {\n"
            "    color: #222;\n"
            "    background: #fff;\n"
            "}"
        )
        self.extract_id.setObjectName("extract_id")
        self.extract_id.clicked.connect(lambda: self.show_popup(generate_IDs))
        self.verticalLayout.addWidget(self.extract_id)
        self.draw_boxes = QtWidgets.QPushButton(parent=self.centralwidget)
        self.draw_boxes.setMaximumSize(QtCore.QSize(171, 16777215))
        self.draw_boxes.setStyleSheet(
            ".QPushButton {\n"
            "    font-family: serif;\n"
            "    color: #fff;\n"
            "    background-color: #222;\n"
            "    border: .1em solid #222;\n"
            "    text-transform: lowercase;\n"
            "    padding: .5em 1em;\n"
            "    border-radius: 5px;\n"
            "    font-style: italic;\n"
            "    transition: all .5s ease;\n"
            "    cursor: pointer;\n"
            "    font-size: 2rem;\n"
            "}\n"
            "\n"
            ".QPushButton:hover {\n"
            "    color: #222;\n"
            "    background: #fff;\n"
            "}"
        )
        self.draw_boxes.setObjectName("draw_boxes")
        self.draw_boxes.clicked.connect(lambda: self.show_popup(generate_bounding_boxes))
        self.verticalLayout.addWidget(self.draw_boxes)
        
        self.clear_queue_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.clear_queue_button.setMaximumSize(QtCore.QSize(171, 16777215))
        self.clear_queue_button.setStyleSheet(
            ".QPushButton {\n"
            "    font-family: serif;\n"
            "    color: #fff;\n"
            "    background-color: #222;\n"
            "    border: .1em solid #222;\n"
            "    text-transform: lowercase;\n"
            "    padding: .5em 1em;\n"
            "    border-radius: 5px;\n"
            "    font-style: italic;\n"
            "    transition: all .5s ease;\n"
            "    cursor: pointer;\n"
            "    font-size: 2rem;\n"
            "}\n"
            "\n"
            ".QPushButton:hover {\n"
            "    color: #222;\n"
            "    background: #fff;\n"
            "}")
        self.clear_queue_button.setObjectName("clear_queue_button")
        self.clear_queue_button.setText("Clear Queue")
        self.clear_queue_button.setEnabled(False)
        self.clear_queue_button.clicked.connect(self.clear_queue)
        self.verticalLayout.addWidget(self.clear_queue_button)
        

        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)
        self.graph_image = QtWidgets.QLabel(parent=self.centralwidget)
        self.graph_image.setMaximumSize(QtCore.QSize(690, 480))
        self.graph_image.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.graph_image.setStyleSheet("")
        self.graph_image.setText("")
        self.graph_image.setPixmap(QtGui.QPixmap("gaze_points.png"))
        self.graph_image.setScaledContents(True)
        self.graph_image.setObjectName("graph_image")
        self.gridLayout.addWidget(self.graph_image, 1, 0, 1, 1)
        self.progress_container = QtWidgets.QVBoxLayout()
        self.gridLayout.addLayout(self.progress_container, 4, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 150, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.help_icon = QtWidgets.QToolButton(parent=self.centralwidget)
        self.help_icon.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.help_icon.setObjectName("help_icon")
        self.help_icon.clicked.connect(lambda: self.show_popup(help_box))
        self.horizontalLayout.addWidget(self.help_icon)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 917, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.generate_plot.setToolTip(
            _translate(
                "MainWindow",
                "<html><head/><body><p>Click to upload a video and corresponding gaze data (CSV format) for processing</p></body></html>",
            )
        )
        self.generate_plot.setText(_translate("MainWindow", "Generate Plot"))
        self.extract_id.setToolTip(
            _translate(
                "MainWindow",
                "<html><head/><body><p>Upload a CSV (gaze data), a JSON file, and a video to extract segments where the user was looking at a specific person.</p></body></html>",
            )
        )
        self.extract_id.setText(_translate("MainWindow", "Extract ID"))
        self.draw_boxes.setToolTip(
            _translate(
                "MainWindow",
                "<html><head/><body><p>Processes a video and generates an annotated version with bounding boxes, along with a json file.</p></body></html>",
            )
        )
        self.draw_boxes.setText(_translate("MainWindow", "See Bounding Boxes"))
        self.help_icon.setText(_translate("MainWindow", "?"))

    def show_popup(self, function):
        # Create an instance of the popup dialog class
        self.dialog = function()  # Pass the class (e.g., generate_graph_popup) as the function
        
        # Set up the UI for the popup
        self.dialog.setupUi(self.dialog)  # Setup the dialog's UI
        
        # Connect the signal to the receiver method (e.g., receive_data)
        self.dialog.value_signal.connect(self.receive_data)

        # Show the popup dialog
        self.dialog.exec()  # This will block execution until the dialog is closed
        self.add_task()
        
    
    def add_task(self):
        id_ = -1
        if self.button == 'extract_id':
            id_, ok = QInputDialog.getInt(None, "Enter ID", "Please enter a number for the ID:")
        queue_item = {
                "json_path": self.json_path,
                "video_path": self.video_path,
                "gaze_path": self.gaze_path,
                "button": self.button, 
                "id": id_,
            }
        self.json_path = ''
        self.video_path = ''
        self.gaze_path = ''
        self.button = ''
        if(self.queue != []):
            self.queue.append(queue_item)
            self.clear_queue_button.setEnabled(True)
        else:
            self.start_task(queue_item)
            

    def start_task(self, queue_item):
        # Create a QWidget to hold the progress bar and label together
        task_widget = QtWidgets.QWidget()
        task_layout = QtWidgets.QVBoxLayout(task_widget)  # Use QVBoxLayout for label + progress bar
        
        # Create a label for displaying the task's video path and progress percentage
        filename = os.path.basename(queue_item["video_path"])
        task_label = QtWidgets.QLabel()
        task_label.setText(f"Task: {filename} - Progress: 0%")
        task_layout.addWidget(task_label)

        # Create a new progress bar for this task
        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        progress_bar.setProperty("value", 0)
        task_layout.addWidget(progress_bar)

        # Add the task widget (containing label and progress bar) to the layout
        self.progress_container.addWidget(task_widget)
    
        if queue_item["button"] == "generate_graph":
                self.start_graph_task(queue_item["json_path"], queue_item["video_path"], queue_item["gaze_path"], progress_bar, task_label)
        elif queue_item["button"] == "extract_id":
                id_, ok = QInputDialog.getInt(None, "Enter ID", "Please enter a number for the ID:")
                self.start_id_extraction(queue_item["json_path"], queue_item["video_path"], queue_item["gaze_path"], queue_item["id_"], progress_bar, task_label)
        elif queue_item["button"] == "bounding_boxes":
                self.start_bounding_task(queue_item["json_path"], queue_item["video_path"], progress_bar, task_label)
                
    def receive_data(self, data):
        """Receive data from the popup window and set the paths."""
        if 'video_path' in data:
            self.video_path = data['video_path']
        if 'json_path' in data:
            self.json_path = data['json_path']
        if 'gaze_path' in data:
            self.gaze_path = data['gaze_path']
        if 'button' in data:
            self.button = data['button']
        # Update the label with the received paths


    def start_id_extraction(self, json_path, video_path, gaze_path, id_, progress_bar, task_label):
        # Create the worker instance
        self.worker = Worker(extract_function, json_path, video_path, gaze_path, id_)

        # Connect the worker signals to your methods
        self.worker.show_video.connect(self.show_video)
        self.worker.progress.connect(lambda value: self.update_progress(progress_bar, task_label, value))  # Pass the progress bar and label
        self.worker.finished.connect(lambda result: self.on_id_completed(progress_bar, task_label, result))  # Handle when the task is done
        self.worker.error.connect(self.on_task_error)  # Handle errors

        # Start the worker thread
        self.worker.start()
        
    def start_bounding_task(self, json_path, video_path, progress_bar,task_label):
        # Create the worker instance
        self.worker = Worker(bounding_function, json_path, video_path)

        # Connect the worker signals to your methods
        self.worker.show_video.connect(self.show_video)
        self.worker.progress.connect(lambda value: self.update_progress(progress_bar, task_label, value))  # Pass the progress bar and label
        self.worker.finished.connect(lambda result: self.on_id_completed(progress_bar, task_label, result))  # Handle when the task is done
        self.worker.error.connect(self.on_task_error)  # Handle errors

        # Start the worker thread
        self.worker.start()
        
        
    def start_graph_task(self, json_path, video_path, gaze_path, progress_bar, task_label):
        # Create the worker instance
        self.worker = Worker(graph_function, json_path, video_path, gaze_path)

        # Connect the worker signals to your methods
        self.worker.show_video.connect(self.show_video)
        self.worker.progress.connect(lambda value: self.update_progress(progress_bar, task_label, value))  # Pass the progress bar and label
        self.worker.finished.connect(lambda result: self.on_graph_completed(progress_bar, task_label, result))  # Handle when the task is done
        self.worker.error.connect(self.on_graph_error)  # Handle errors

        # Start the worker thread
        self.worker.start()

    def on_id_completed(self, progress_bar, task_label, value):
        self.button = ''
        # Get the parent widget that contains both the progress bar and label
        task_widget = progress_bar.parentWidget()
        # Remove the widget from the layout
        self.progress_container.removeWidget(task_widget)
        task_widget.deleteLater()  # Delete the widget (which contains the progress bar and label)

        if self.queue != []:
            self.start_task(self.queue.pop(0))
        else:
            self.clear_queue_button.setEnabled(False)
        # Update the UI with the result (e.g., show a message or display the graph)
    def update_progress(self, progress_bar, task_label, value):
        """Update a progress bar based on progress emitted by the worker."""
        progress_bar.setProperty("value", value)
        task_label.setText(f"{task_label.text().split('-')[0]}- Progress: {value}%")
        # You can update a progress bar widget here, e.g., self.progressBar.setValue(value)

    def on_graph_completed(self, progress_bar, task_label, value):
        self.graph_image.setPixmap(QtGui.QPixmap(value))
        task_widget = progress_bar.parentWidget()

        # Remove the widget from the layout
        self.progress_container.removeWidget(task_widget)
        task_widget.deleteLater()  # Delete the widget (which contains the progress bar and label)

        if self.queue != []:
            self.start_task(self.queue.pop(0))
        else:
            self.clear_queue_button.setEnabled(False)
        # Update the UI with the result (e.g., show a message or display the graph)

    def on_graph_error(self, error_message):
        """Handle errors raised during the execution."""
        print(f"Error: {error_message}")

    def show_video(self, video_path, bbox_file_path):
        # Create and show your video window with the provided paths
        video_annotator = VideoAnnotator(video_path, bbox_file_path)
        video_annotator.show()

        # Connect the close event of the video window to resume the worker thread
        video_annotator.closed.connect(self.worker.resume_from_video)
        
    def clear_queue(self):
        self.queue = []
        self.clear_queue_button.setEnabled(False)
        

def bounding_function(progress, json_path, video_path):
        if json_path == '':
            output_path, results, rotate_amount = run_detection(video_path, progress)
            json_file, processed_video_path = reID(output_path, results, rotate_amount, progress)
            video_annotator = VideoAnnotator(processed_video_path, json_file)
            video_annotator.show()  # Launch VideoAnnotator in a separate window
        else:
            progress.emit(50)
            draw_boxes_from_pkl(json_path, video_path)
            
            
        

def extract_function(progress,show_video_signal, worker, json_path, video_path, gaze_path, id_):
        if json_path == '':
            output_path, results, rotate_amount = run_detection(video_path, progress)
            json_file, processed_video_path = reID(output_path, results, rotate_amount, progress)
            show_video_signal.emit(video_path, json_file)
            worker._mutex.lock()
            worker._pause_condition.wait(worker._mutex)
            worker._mutex.unlock()
            plot = initialize_plot_data(json_file, gaze_path)
            generate_compilation_from_frames(processed_video_path, plot.data, id_)
        else:
            progress.emit(10)
            plot = initialize_plot_data(json_path, gaze_path)
            progress.emit(80)
            generate_compilation_from_frames(video_path, plot.data, id_)
            progress.emit(99)
        
def graph_function(progress, show_video_signal,worker, json_path, video_path, gaze_path):
        if json_path == '':
                output_path, results, rotate_amount = run_detection(video_path, progress)
                json_file, processed_video_path = reID(output_path, results, rotate_amount, progress)
                show_video_signal.emit(video_path, json_file)
                worker._mutex.lock()
                worker._pause_condition.wait(worker._mutex)
                worker._mutex.unlock()
                plot = initialize_plot_data(json_file, gaze_path)
                graph_path = generate_graph(plot, os.path.splitext(os.path.basename(video_path))[0])
                return graph_path
        else:
                progress.emit(10)
                plot = initialize_plot_data(json_path, gaze_path)
                progress.emit(80)
                graph_path = generate_graph(plot, os.path.splitext(json_path.replace("bounding_boxes_rotated_", ""))[0])
                progress.emit(99)
                return graph_path
        
        
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
