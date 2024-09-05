from dataclasses import dataclass
from PySide6 import QtCore, QtWidgets, QtGui
import sys
from models.event_bus import EventBus



class FlowchartEditor:
    def __init__ (self, event_bus: EventBus):
        self.__event_bus = event_bus
        self.run()
        
    def run(self):
        self.__event_bus.on("app:initalize", self.handleInitalize)
        
    def handleInitalize(self, arguments):
        app = QtWidgets.QApplication(sys.argv)
        window = FlowchartWidget()
        window.setWindowTitle("Flowchart Proof of Concept")
        window.show()
        sys.exit(app.exec())


class FlowchartWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.box1 = ProcessLabel("Box 1", self)
        self.box2 = ProcessLabel("Box 2", self)
        self.box1.move(50, 50)
        self.box2.move(200, 200)
        self.line_start_pos = None
        self.line_end_pos = None
        self.setFixedSize(400, 300)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.line_start_pos and self.line_end_pos:
            painter = QtGui.QPainter(self)
            pen = QtGui.QPen(QtGui.QColor('black'), 2)
            painter.setPen(pen)
            painter.drawLine(self.line_start_pos, self.line_end_pos)

    def mousePressEvent(self, event):
        # Reset the line positions on mouse click
        self.line_start_pos = None
        self.line_end_pos = None
        self.update()
    
class ProcessLabel(QtWidgets.QLabel):    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFixedSize(100, 60)
        self.setStyleSheet("background-color: lightblue; border: 1px solid black;")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMouseTracking(True)
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = self.mapToParent(event.pos())

    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.parent().line_start_pos = self.start_pos
            self.parent().line_end_pos = self.mapToParent(event.pos())
            self.parent().update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = None
            self.parent().line_end_pos = self.mapToParent(event.pos())
            self.parent().update()