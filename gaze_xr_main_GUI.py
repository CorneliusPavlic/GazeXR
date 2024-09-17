
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
from swapBoundingBoxes import VideoAnnotator

class Worker(QThread):
    progress = pyqtSignal(int)  # Signal to emit progress updates
    finished = pyqtSignal(str)  # Signal to emit when the task is complete
    error = pyqtSignal(str)  # Signal to emit errors

    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task  # The task (function) to be executed
        self.args = args  # Positional arguments for the task
        self.kwargs = kwargs  # Keyword arguments for the task

    def run(self):
        """Run the provided task in a separate thread."""
        try:
            result = self.task(self.progress, *self.args, **self.kwargs)  # Execute the task
            self.finished.emit(result)   # Emit finished signal when done
        except Exception as e:
            self.error.emit(str(e))  # Emit error signal if an exception occurs

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

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
        self.progress_bar = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progress_bar.setEnabled(True)
        self.progress_bar.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName("progress_bar")
        self.gridLayout.addWidget(self.progress_bar, 4, 0, 1, 1)
        self.progress_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.progress_label.setObjectName("progress_label")
        self.gridLayout.addWidget(self.progress_label, 4, 1, 1, 1)
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
        self.progress_label.setText(
            _translate("MainWindow", "Progress: 0% (estimated time: 0:00)")
        )
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
        
        if self.button == "generate_graph":
                self.start_graph_task(self.json_path, self.video_path, self.gaze_path)
        elif self.button == "extract_id":
                id_, ok = QInputDialog.getInt(None, "Enter ID", "Please enter a number for the ID:")
                self.start_id_extraction(self.json_path, self.video_path, self.gaze_path, id_)
        elif self.button == "bounding_boxes":
                self.start_bounding_task(self.json_path, self.video_path)
                
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


    def start_id_extraction(self, json_path, video_path, gaze_path, id_):
        # Create the worker instance
        self.worker = Worker(extract_function, json_path, video_path, gaze_path, id_)

        # Connect the worker signals to your methods
        self.worker.progress.connect(self.update_progress)  # To update a progress bar or similar
        self.worker.finished.connect(self.on_id_completed)  # Handle when the task is done
        self.worker.error.connect(self.on_graph_error)  # Handle errors

        # Start the worker thread
        self.worker.start()
        
    def start_bounding_task(self, json_path, video_path):
        # Create the worker instance
        self.worker = Worker(bounding_function, json_path, video_path)

        # Connect the worker signals to your methods
        self.worker.progress.connect(self.update_progress)  # To update a progress bar or similar
        self.worker.finished.connect(self.on_id_completed)  # Handle when the task is done
        self.worker.error.connect(self.on_graph_error)  # Handle errors

        # Start the worker thread
        self.worker.start()
        
        
    def start_graph_task(self, json_path, video_path, gaze_path):
        # Create the worker instance
        self.worker = Worker(graph_function, json_path, video_path, gaze_path)

        # Connect the worker signals to your methods
        self.worker.progress.connect(self.update_progress)  # To update a progress bar or similar
        self.worker.finished.connect(self.on_graph_completed)  # Handle when the task is done
        self.worker.error.connect(self.on_graph_error)  # Handle errors

        # Start the worker thread
        self.worker.start()

    def on_id_completed(self, value):
        self.progress_bar.setProperty("value", 0)
        self.progress_label.setText("Progress: {}%".format(0))
        self.button = ''
        # Update the UI with the result (e.g., show a message or display the graph)
    def update_progress(self, value):
        """Update a progress bar based on progress emitted by the worker."""
        self.progress_bar.setProperty("value", value)
        self.progress_label.setText("Progress: {}%".format(value))
        # You can update a progress bar widget here, e.g., self.progressBar.setValue(value)

    def on_graph_completed(self, value):
        self.button = ''
        self.progress_bar.setProperty("value", 0)
        self.progress_label.setText("Progress: {}%".format(0))
        self.graph_image.setPixmap(QtGui.QPixmap(value))
        # Update the UI with the result (e.g., show a message or display the graph)

    def on_graph_error(self, error_message):
        """Handle errors raised during the execution."""
        print(f"Error: {error_message}")


def bounding_function(progress, json_path, video_path):
        if json_path == '':
            output_path, results, rotate_amount = run_detection(video_path, progress)
            json_file, processed_video_path = reID(output_path, results, rotate_amount, progress)
        else:
            progress.emit(50)
            draw_boxes_from_pkl(json_path, video_path)
            
            
        

def extract_function(progress, json_path, video_path, gaze_path, id_):
        if json_path == '':
            output_path, results, rotate_amount = run_detection(video_path, progress)
            json_file, processed_video_path = reID(output_path, results, rotate_amount, progress)
            plot = initialize_plot_data(json_file, gaze_path)
            generate_compilation_from_frames(processed_video_path, plot.data, id_)
        else:
            progress.emit(10)
            plot = initialize_plot_data(json_path, gaze_path)
            progress.emit(80)
            generate_compilation_from_frames(video_path, plot.data, id_)
            progress.emit(99)
        
def graph_function(progress, json_path, video_path, gaze_path):
        if json_path == '':
                output_path, results, rotate_amount = run_detection(video_path, progress)
                json_file, processed_video_path = reID(output_path, results, rotate_amount, progress)
                plot = initialize_plot_data(json_file, gaze_path)
                graph_path = generate_graph(plot)
                return graph_path
        else:
                progress.emit(10)
                plot = initialize_plot_data(json_path, gaze_path)
                progress.emit(80)
                graph_path = generate_graph(plot)
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
