# -*- coding: utf-8 -*-
import logging
import datetime
from PyQt5.QtWidgets import QWidget, QTextEdit
from PyQt5.QtGui import QKeySequence

class TextLogger(logging.Handler):
    def __init__(self, parent: QWidget = None):
        super(TextLogger, self).__init__()
        self.widget = QTextEdit()
        self.widget.setReadOnly(True)
        self.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S'))

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)