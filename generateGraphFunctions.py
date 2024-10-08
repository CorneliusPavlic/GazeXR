from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QDialog
from PyQt6.QtCore import QThread, pyqtSignal



class generate_graph_popup(QDialog):
    value_signal = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)   # Initialize QDialog parent class
        self.video_path = ''
        self.json_path = ''
        self.gaze_path = ''
        self.setupUi(self)
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("background-color: rgb(75, 75, 75);")
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 376, 181))
        self.label.setMaximumSize(QtCore.QSize(16777215, 181))
        self.label.setStyleSheet("color: #aaaaaa")
        self.label.setObjectName("label")
        self.generate_graph_scratch = QtWidgets.QPushButton(parent=Dialog)
        self.generate_graph_scratch.setGeometry(QtCore.QRect(10, 220, 188, 36))
        self.generate_graph_scratch.setStyleSheet(".QPushButton {\n"
"    font-family: serif;\n"
"    color: #fff;\n"
"    background-color: #222;\n"
"    border: .1em solid #222;\n"
"\n"
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
"}")
        self.generate_graph_scratch.setObjectName("generate_graph_scratch")
        self.generate_graph_json = QtWidgets.QPushButton(parent=Dialog)
        self.generate_graph_json.setGeometry(QtCore.QRect(210, 220, 174, 36))
        self.generate_graph_json.setStyleSheet(".QPushButton {\n"
"    font-family: serif;\n"
"    color: #fff;\n"
"    background-color: #222;\n"
"    border: .1em solid #222;\n"
"\n"
"    padding: .5em 1em;\n"
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
"}")
        self.generate_graph_json.setObjectName("generate_graph_json")
        self.generate_graph_scratch.clicked.connect(self.generate_graph_scratch_clicked)
        self.generate_graph_json.clicked.connect(self.generate_graph_json_clicked)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p align=\"center\">Do you have a .JSON file? </p><p align=\"center\">If not select Video and it will generate one</p><p align=\"center\">as well as drawing your bounding boxes</p></body></html>"))
        self.generate_graph_scratch.setText(_translate("Dialog", "I have a Video"))
        self.generate_graph_json.setText(_translate("Dialog", "I have the JSON file"))
        
        
        
    def generate_graph_scratch_clicked(self, parent):
        """Open file dialogs to select video and JSON files."""
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video files (*.mp4 *.avi *.mov)")
        self.gaze_path, _ = QFileDialog.getOpenFileName(self, "Select Gaze Data File", "", "CSV files (*.csv)")
        if self.video_path and self.gaze_path:
            # Emit both file paths as a dictionary
            self.value_signal.emit({'video_path': self.video_path, 'gaze_path': self.gaze_path, 'button': 'generate_graph'})
            self.accept()
        else:
            self.value_signal.emit({'button': 'failed'})
    def generate_graph_json_clicked(self, parent):
        """Open file dialogs to select video and JSON files."""
        self.json_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON files (*.json)")
        self.gaze_path, _ = QFileDialog.getOpenFileName(self, "Select Gaze Data File", "", "CSV files (*.csv)")
        if self.json_path and self.gaze_path:
            # Emit both file paths as a dictionary
            self.value_signal.emit({'video_path': self.video_path, 'gaze_path': self.gaze_path, 'json_path': self.json_path, 'button': 'generate_graph'})
            self.accept()
        else:
            self.value_signal.emit({'button': 'failed'})


class generate_IDs(QDialog):
    value_signal = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)   # Initialize QDialog parent class
        self.video_path = ''
        self.json_path = ''
        self.gaze_path = ''
        self.setupUi(self)
        
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("background-color: rgb(75, 75, 75);")
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 376, 181))
        self.label.setMaximumSize(QtCore.QSize(16777215, 181))
        self.label.setStyleSheet("color: #aaaaaa")
        self.label.setObjectName("label")
        self.extract_id_scratch = QtWidgets.QPushButton(parent=Dialog)
        self.extract_id_scratch.setGeometry(QtCore.QRect(10, 220, 188, 36))
        self.extract_id_scratch.setStyleSheet(".QPushButton {\n"
"    font-family: serif;\n"
"    color: #fff;\n"
"    background-color: #222;\n"
"    border: .1em solid #222;\n"
"\n"
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
"}")
        self.extract_id_scratch.setObjectName("extract_id_scratch")
        self.extract_id_json = QtWidgets.QPushButton(parent=Dialog)
        self.extract_id_json.setGeometry(QtCore.QRect(210, 220, 174, 36))
        self.extract_id_json.setStyleSheet(".QPushButton {\n"
"    font-family: serif;\n"
"    color: #fff;\n"
"    background-color: #222;\n"
"    border: .1em solid #222;\n"
"\n"
"    padding: .5em 1em;\n"
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
"}")
        self.extract_id_json.setObjectName("extract_id_json")
        self.extract_id_scratch.clicked.connect(self.on_extract_id_scratch_clicked)
        self.extract_id_json.clicked.connect(self.on_extract_id_json_clicked)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">This will require an original video, and Gaze data. <br/>If you would like the process to go faster you can also</span></p><p align=\"center\"><span style=\" font-size:12pt;\">supply a .json file.</span></p></body></html>"))
        self.extract_id_scratch.setText(_translate("Dialog", "generate everything"))
        self.extract_id_json.setText(_translate("Dialog", "I have the json file"))
        
        
    def on_extract_id_scratch_clicked(self, parent):
        """Open file dialogs to select video and JSON files."""
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video files (*.mp4 *.avi *.mov)")
        self.gaze_path, _ = QFileDialog.getOpenFileName(self, "Select Gaze Data File", "", "CSV files (*.csv)")
        
        if self.video_path and self.gaze_path:
            # Emit both file paths as a dictionary
            self.value_signal.emit({'video_path': self.video_path, 'gaze_path' : self.gaze_path, 'button': 'extract_id'})
            self.accept()
        else:
            self.value_signal.emit({'button': 'failed'})
            
    def on_extract_id_json_clicked(self, parent):
        """Open file dialogs to select video and JSON files."""
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video files (*.mp4 *.avi *.mov)")
        self.json_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON files (*.json)")
        self.gaze_path, _ = QFileDialog.getOpenFileName(self, "Select Gaze Data File", "", "CSV files (*.csv)")
        if self.json_path and self.video_path and self.gaze_path:
            # Emit both file paths as a dictionary
            self.value_signal.emit({'video_path': self.video_path, 'gaze_path' : self.gaze_path, 'json_path': self.json_path, 'button': 'extract_id'})
            self.accept()
        else:
            self.value_signal.emit({'button': 'failed'})


class generate_bounding_boxes(QDialog):
    value_signal = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)   # Initialize QDialog parent class
        self.video_path = ''
        self.json_path = ''
        self.gaze_path = ''
        self.setupUi(self)
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("background-color: rgb(75, 75, 75);")
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 376, 181))
        self.label.setMaximumSize(QtCore.QSize(16777215, 181))
        self.label.setStyleSheet("color: #aaaaaa")
        self.label.setObjectName("label")
        self.extract_id_scratch = QtWidgets.QPushButton(parent=Dialog)
        self.extract_id_scratch.setGeometry(QtCore.QRect(10, 220, 188, 36))
        self.extract_id_scratch.setStyleSheet(".QPushButton {\n"
"    font-family: serif;\n"
"    color: #fff;\n"
"    background-color: #222;\n"
"    border: .1em solid #222;\n"
"\n"
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
"}")
        self.extract_id_scratch.setObjectName("extract_id_scratch")
        self.extract_id_json = QtWidgets.QPushButton(parent=Dialog)
        self.extract_id_json.setGeometry(QtCore.QRect(210, 220, 174, 36))
        self.extract_id_json.setStyleSheet(".QPushButton {\n"
"    font-family: serif;\n"
"    color: #fff;\n"
"    background-color: #222;\n"
"    border: .1em solid #222;\n"
"\n"
"    padding: .5em 1em;\n"
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
"}")
        self.extract_id_json.setObjectName("extract_id_json")
        self.extract_id_scratch.clicked.connect(self.on_extract_id_scratch_clicked)
        self.extract_id_json.clicked.connect(self.on_extract_id_json_clicked)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p align=\"center\">Do you have a .JSON file? </p><p align=\"center\">If not select Video and it will generate one</p><p align=\"center\">as well as drawing your bounding boxes</p></body></html>"))
        self.extract_id_scratch.setText(_translate("Dialog", "I have a Video"))
        self.extract_id_json.setText(_translate("Dialog", "I have the JSON file"))

    def on_extract_id_scratch_clicked(self, parent):
        """Open file dialogs to select video and JSON files."""
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video files (*.mp4 *.avi *.mov)")
        if self.video_path:
            # Emit both file paths as a dictionary
            self.value_signal.emit({'video_path': self.video_path, 'button': 'bounding_boxes'})
            self.accept()
        else:
            self.value_signal.emit({'button': 'failed'})
            
    def on_extract_id_json_clicked(self, parent):
        """Open file dialogs to select video and JSON files."""
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video files (*.mp4 *.avi *.mov)")
        self.json_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON files (*.json)")
        if self.json_path and self.video_path:
            # Emit both file paths as a dictionary
            self.value_signal.emit({'video_path': self.video_path, 'json_path': self.json_path, 'button': 'bounding_boxes'})
            self.accept()
        else:
            self.value_signal.emit({'button': 'failed'})

class help_box(QDialog):
    value_signal = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)   # Initialize QDialog parent class
        self.setupUi(self)
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(551, 300)
        Dialog.setStyleSheet("background-color: rgb(75, 75, 75);")
        self.label = QtWidgets.QLabel(parent=Dialog)
        self.label.setGeometry(QtCore.QRect(0, 0, Dialog.width(), Dialog.height()))
        self.label.setObjectName("label")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p align=\"center\">Hello, Welcome to GazeXR. Here you\'ll be able to generate</p><p align=\"center\">Graphs, Draw bounding boxes on videos, and extract</p><p align=\"center\">the points of interest from Gaze Data. </p><p align=\"center\">We use .JSON files to save the bounding boxes from the videos.</p><p align=\"center\">This allow for the sharing of videos and quick </p><p align=\"center\">and easy loading after the intial detection. </p><p align=\"center\"><br/></p><p align=\"center\">To get started click the generate graph button </p><p align=\"center\">and follow the prompts</p></body></html>"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = generate_graph_popup()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())

