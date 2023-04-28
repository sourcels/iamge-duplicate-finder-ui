import os, sys, shutil, json, cv2, logging
from pathlib import Path
from typing import Optional, Dict, List
from duplicate_worker import DuplicateWorker
from text_logger import TextLogger

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStyle, QDesktopWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QListWidget, QLabel, QListWidgetItem, QMenu, QMessageBox, QColorDialog, QDialog, QTabWidget, QCheckBox, QSpinBox, QLineEdit, QFileDialog, QMenuBar, QAction, QMenu, QScrollArea
from PyQt5.QtCore import Qt, QDir, QFile, QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QStandardItemModel, QStandardItem


class Main(QMainWindow):
    def __init__(self, parent: QWidget = None) -> None:
        super(Main, self).__init__(parent)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(TextLogger(self))

        self.logger.info("Program start")

        self.setWindowTitle("Duplicate finder")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.input_folder_label = QLabel("Source Folder:")
        self.main_layout.addWidget(self.input_folder_label, 0, 0, Qt.AlignRight)
        self.input_folder_button = QPushButton(self.style().standardIcon(QStyle.SP_DirOpenIcon), "Open Folder")
        self.input_folder_button.setObjectName("input_folder")
        self.input_folder_button.clicked.connect(self.open_input_folder)
        self.main_layout.addWidget(self.input_folder_button, 0, 1, Qt.AlignLeft)

        self.output_folder_label = QLabel("Output Folder:")
        self.main_layout.addWidget(self.output_folder_label, 1, 0, Qt.AlignRight)
        self.output_folder_button = QPushButton(self.style().standardIcon(QStyle.SP_DirOpenIcon), "Open Folder")
        self.output_folder_button.setObjectName("output_folder")
        self.output_folder_button.clicked.connect(self.open_output_folder)
        self.main_layout.addWidget(self.output_folder_button, 1, 1, Qt.AlignLeft)

        self.input_threshold_label = QLabel("Threshold:")
        self.main_layout.addWidget(self.input_threshold_label, 2, 0, Qt.AlignRight)
        self.input_threshold_spinbox = QSpinBox()
        self.input_threshold_spinbox.setMinimum(0)
        self.input_threshold_spinbox.setMaximum(100)
        self.input_threshold_spinbox.setSuffix("%")
        self.input_threshold_spinbox.setObjectName("input_threshold")
        self.main_layout.addWidget(self.input_threshold_spinbox, 2, 1, Qt.AlignLeft)

        self.input_hashSize_label = QLabel("Hash Size:")
        self.main_layout.addWidget(self.input_hashSize_label, 3, 0, Qt.AlignRight)
        self.input_hashSize_spinbox = QSpinBox()
        self.input_hashSize_spinbox.setMinimum(16)
        self.input_hashSize_spinbox.setMaximum(256)
        self.input_hashSize_spinbox.setObjectName("input_hashSize")
        self.main_layout.addWidget(self.input_hashSize_spinbox, 3, 1, Qt.AlignLeft)

        self.image_label = QLabel()
        self.image_label.setStyleSheet('border: 2px solid black; padding: 2px;')
        self.image_label.setFixedSize(400, 400)
        self.image_label.setPixmap(QPixmap())
        self.main_layout.addWidget(self.image_label, 0, 2, 0, 4, Qt.AlignLeft)

        self.log_label = QLabel()
        self.log_label.setWordWrap(True)
        self.log_label.setFixedWidth(600)
        self.log_label.setText(self.logger.handlers[0].widget.toPlainText())

        self.scroll_log_label = QScrollArea()
        self.scroll_log_label.setWidget(self.log_label)
        self.scroll_log_label.setMinimumWidth(200)
        self.scroll_log_label.setWidgetResizable(True)
        self.scroll_log_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_log_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_layout.addWidget(self.scroll_log_label, 0, 3, 0, 4, Qt.AlignRight)

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("start_process")
        self.start_button.clicked.connect(self.start_process)
        self.main_layout.addWidget(self.start_button, 4, 0, Qt.AlignLeft)

        self.main_layout.setColumnStretch(2, 1)
        self.main_layout.setRowStretch(3, 1)

        menubar = QMenuBar(self)
        file_menu = QMenu('&File', self)
        menubar.addMenu(file_menu)
        open_input_action = QAction('&Open Folder to check for duplicates', self)
        open_input_action.setShortcut('Ctrl+I')
        open_input_action.triggered.connect(self.open_input_folder)
        file_menu.addAction(open_input_action)
        open_output_action = QAction('&Open Folder to move duplicates', self)
        open_output_action.setShortcut('Ctrl+O')
        open_output_action.triggered.connect(self.open_output_folder)
        file_menu.addAction(open_output_action)

        self.setMenuBar(menubar)

    def open_input_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Choose folder to check")
        if folder_path:
            self.input_folder_label.setToolTip(folder_path)
            self.input_folder_button.setToolTip(folder_path)
            self.logger.info(f"Selected folder to process: {folder_path}")
            self.log_label.setText(self.logger.handlers[0].widget.toPlainText())

    def open_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Choose folder to move duplicates")
        if folder_path:
            self.output_folder_label.setToolTip(folder_path)
            self.output_folder_button.setToolTip(folder_path)
            self.logger.info(f"Selected folder to move duplicates: {folder_path}")
            self.log_label.setText(self.logger.handlers[0].widget.toPlainText())

    def start_process(self):
        try:
            DuplicateWorker(source_folder_path=self.input_folder_label.toolTip(), duplicate_folder_path=self.output_folder_label.toolTip(), threshold=self.input_threshold_spinbox.value(), hash_size=self.input_hashSize_spinbox.value(), parent=self)
            self.image_label.setPixmap(QPixmap())
        except FileNotFoundError:
            self.logger.critical("Can't run process! No folders chosen.")
            self.log_label.setText(self.logger.handlers[0].widget.toPlainText())
            QMessageBox.critical(self, "Folder Error", "Please choose directories.")
        # except Exception as err:
        #     self.logger.critical(err)
        #     self.log_label.setText(self.logger.handlers[0].widget.toPlainText())
        #     QMessageBox.critical(self, "Unexpected Error!", f"Details: {err}")
        self.image_label.setPixmap(QPixmap())

    def resizeEvent(self, event):
        size = event.size()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())