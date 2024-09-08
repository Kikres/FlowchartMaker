from dataclasses import dataclass
from typing import List
from PySide6 import QtCore, QtWidgets, QtGui
from models.event_bus import EventBus
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QPoint, QRect
import sys
import math


class FlowchartEditor:
    def __init__(self, event_bus: EventBus):
        self.__event_bus = event_bus
        self.run()

    def run(self):
        self.__event_bus.on("app:initialize", self.handle_initialize)

    def handle_initialize(self, arguments=None):
        self.window = FlowchartWindow()
        self.window.setWindowTitle("Flowchart Proof of Concept")
        self.window.show()
       # Custom class to represent a flowchart shape (base class)



# Custom class to represent the flowchart creation window
class FlowchartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flowchart Creator")
        self.setGeometry(100, 100, 800, 600)
        self.arrow_start = None  # Starting point for the arrow
        self.arrow_end = None  # End point for the arrow
        self.shapes = [Decision(self), Decision(self)]  # Add shapes

        # Position shapes
        self.shapes[0].move(200, 150)
        self.shapes[1].move(400, 300)

        print("Flowchart Window initialized")

    def mousePressEvent(self, event):
        # Check each shape for an active node and set the arrow start point
        for shape in self.shapes:
            if shape.active_node:
                self.arrow_start = shape.mapToParent(shape.active_node)
                print("Arrow started at:", self.arrow_start)

    def mouseMoveEvent(self, event):
        # Update the arrow end point as the mouse moves
        if self.arrow_start:
            self.arrow_end = event.pos()
            self.update()  # Trigger repaint

    def mouseReleaseEvent(self, event):
        # Clear the arrow on mouse release
        self.arrow_start = None
        self.arrow_end = None
        self.update()

    def paintEvent(self, event):
        # Custom paint logic to draw the arrow
        super().paintEvent(event)
        if self.arrow_start and self.arrow_end:
            painter = QPainter(self)
            pen = QPen(Qt.black, 2)
            painter.setPen(pen)
            painter.drawLine(self.arrow_start, self.arrow_end)  # Draw the arrow
        
        


class Node:
    def __init__(self, parent: QWidget, qpoint: QPoint, radius: int):
        self.parent = parent
        self.qpoint = qpoint
        self.radius = radius
        self.active = False
        
    def get_offset_position(self):
        qpoint_offset = QPoint(self.parent.width() // 2, self.parent.height() // 2)
        return self.qpoint + qpoint_offset
        
           
    
    
class Arrow(QWidget):
    def __init__(self, parent, start: Node, end: Node):
        super().__init__(parent)
        self.start = start
        self.end = end
        self.setFixedSize(parent.size())
        self.setAttribute(Qt.WA_TransparentForMouseEvents) 
        
    def paintEvent(self, event):
        print("Drawing line", self)
        with QPainter(self) as painter:
            pen = QtGui.QPen(QtGui.QColor('black'), 2)
            painter.setPen(pen)
            painter.drawLine(self.mapToParent(self.start.get_offset_position()), self.end)
            
class Shape(QWidget):
    def __init__(self, parent: FlowchartWindow, width, height, string: str, node_positions: List[QPoint], node_radius: int):
        super().__init__(parent)
        self.string = string
        self.locked = False
        self.active_node = None
        self.node_positions = node_positions
        self.node_radius = node_radius
        self.setFixedSize(width + node_radius * 2, height + node_radius * 2)
        self.setMouseTracking(True)
        
    def get_offset_qpoint(self, qpoint: QPoint):
        qpoint_offset = QPoint(self.width() // 2, self.height() // 2)
        return (qpoint + qpoint_offset)
    
    def paintEvent(self, event):
        for node_position in self.node_positions:
            with QPainter(self) as painter:
                painter.setPen(Qt.NoPen)

                if self.active_node == self.get_offset_qpoint(node_position):
                    painter.setBrush(QBrush(QColor(255, 255, 0)))  # Yellow when active
                else:
                    painter.setBrush(Qt.BrushStyle.NoBrush)

                painter.drawEllipse(self.get_offset_qpoint(node_position), self.node_radius, self.node_radius)    
        
    def mousePressEvent(self, event):
        # Hoist to parent if an active node is set
        if event.button() == Qt.LeftButton and self.active_node:
            self.parent().mousePressEvent(event) 
        # Otherwise handle movement 
        elif event.button() == Qt.LeftButton:
            self.locked = True
            self.drag_start = event.pos()
        # Raise the widget to the top of the stack
        self.raise_()

    def mouseMoveEvent(self, event): 
        mouse_pos = event.pos()
        
        if self.locked:
            self.move(self.mapToParent(mouse_pos - self.drag_start))
            
        self.active_node = None
        for node_position in self.node_positions:
            # Calculate the distance between mouse position and the node's position
            distance = math.hypot(mouse_pos.x() - (self.get_offset_qpoint(node_position).x()),
                                  mouse_pos.y() - (self.get_offset_qpoint(node_position).y()))
            # If the cursor is within the node's radius, set active
            if distance < self.node_radius:
                self.active_node = self.get_offset_qpoint(node_position)
                
        self.update()


    def mouseReleaseEvent(self, event):
        self.locked = False
        # self.parent().mouseReleaseEvent(event, self.active_node)

        
    def leaveEvent (self, event):
        # Deactivate all nodes when the mouse leaves the widget
        self.active_node = None
        # Update the widget to re-render the nodes
        self.update()


### Decision Shape ###

class Decision(Shape):
    def __init__(self, parent):
        width = 130
        height = 80
        label = "Decision"
        node_positions = [
                QPoint(-65, 0),  # Left
                QPoint(65, 0),   # Right
                QPoint(0, 40),   # Bottom
                QPoint(0, -40)   # Top
            ]
        node_radius = 8
        super().__init__(parent, width, height, label, node_positions, node_radius)
        
    def paintEvent(self, event):
        # Render shape
        with QPainter(self) as painter:
            painter.setPen(QPen(Qt.black, 2))

            # Calculate the center of the widget (window)
            center_x = self.width() // 2
            center_y = self.height() // 2

            # Draw a rounded rectangle (Decision)
            painter.drawRoundedRect(center_x - 65, center_y - 40, 130, 80, 40, 40)
        
        super().paintEvent(event)