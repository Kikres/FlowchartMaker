import json
import math
from dataclasses import dataclass
from typing import List
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QInputDialog
)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QPoint, QRect
from models.event_bus import EventBus

@dataclass
class ShapeData:
    shape_type: str
    x: int
    y: int
    width: int
    height: int
    text: str

@dataclass
class ArrowData:
    start_shape_index: int
    start_node_index: int
    end_shape_index: int
    end_node_index: int

class FlowchartEditor:
    def __init__(self, event_bus: EventBus):
        self.__event_bus = event_bus
        self.run()

    def run(self):
        self.__event_bus.on("app:initialize", self.handle_initialize)

    def handle_initialize(self, arguments=None):
        self.window = Window()
        self.window.setWindowTitle("Flowchart Proof of Concept")
        self.window.show()
        
    def handle_load(self):
        print("Load event sent to bus")
        pass
    
    def handle_save(self):
        print("Save event sent to bus")
        pass        
    
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flowchart Creator")
        self.setGeometry(100, 100, 1000, 600) # Initial window size

        # Set the main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Create the flowchart area and toolbar
        self.flowchart_area = Area(self)
        self.toolbar = Toolbar(self)

        # Add flowchart area to the left and toolbar to the right
        layout.addWidget(self.flowchart_area, stretch=4)
        layout.addWidget(self.toolbar, stretch=1)
        
        # Methods to add shapes to the flowchart area
    def handle_add_process(self):
        new_shape = Process(self.flowchart_area)
        self.flowchart_area.add_shape(new_shape)

    def handle_add_decision(self):
        new_shape = Decision(self.flowchart_area)
        self.flowchart_area.add_shape(new_shape)

    def handle_add_terminator(self):
        new_shape = Terminator(self.flowchart_area)
        self.flowchart_area.add_shape(new_shape)

    def handle_add_io(self):
        new_shape = IO(self.flowchart_area)
        self.flowchart_area.add_shape(new_shape)
        
    def handle_save(self):
        file_path = "flowchart.json"  # You can use a file dialog for dynamic paths
        print(self.flowchart_area.save_to_json(file_path))
        print("Flowchart saved to", file_path)

    def handle_load(self):
        file_path = "flowchart.json"  # You can use a file dialog for dynamic paths
        self.flowchart_area.load_from_json(file_path)
        print("Flowchart loaded from", file_path)
        
class Toolbar(QWidget):
    def __init__(self, parent: Window):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Add buttons for shapes
        btn_add_process = QPushButton("Add Process", self)
        btn_add_decision = QPushButton("Add Decision", self)
        btn_add_terminator = QPushButton("Add Terminator", self)
        btn_add_io = QPushButton("Add I/O", self)

        layout.addWidget(btn_add_process)
        layout.addWidget(btn_add_decision)
        layout.addWidget(btn_add_terminator)
        layout.addWidget(btn_add_io)

        # Connect buttons to create shapes in the flowchart area via the FlowchartWindow
        btn_add_process.clicked.connect(self.parent().handle_add_process)
        btn_add_decision.clicked.connect(self.parent().handle_add_decision)
        btn_add_terminator.clicked.connect(self.parent().handle_add_terminator)
        btn_add_io.clicked.connect(self.parent().handle_add_io)

        # Save and Load buttons
        btn_save = QPushButton("Save", self)
        btn_load = QPushButton("Load", self)
        
        btn_save.clicked.connect(self.parent().handle_save)
        btn_load.clicked.connect(self.parent().handle_load)

        layout.addWidget(btn_save)
        layout.addWidget(btn_load)

class Area(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arrow_start = None  # Starting point for the arrow
        self.arrow_end = None  # End point for the arrow
        self.shapes = []
        self.arrows = []
        self.active_shape = None
        self.setMouseTracking(True)
    
    def add_shape(self, shape: QWidget):
        shape.move(self.width() // 2 - shape.width() // 2, self.height() // 2 - shape.height() // 2)  # Center the shape on area
        self.shapes.append(shape)
        shape.show()
        self.update()  # Trigger repaint
    
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return  # Only process left mouse clicks
        
        if self.active_shape:
            mouse_pos = event.pos()
            
            # Handle deletion of shape, ensuring all arrows connected to the shape are deleted
            if self.active_shape.on_cross(mouse_pos):
                self.shapes.remove(self.active_shape)
                self.active_shape.deleteLater()

                # Collect arrows to delete
                arrows_to_delete = [arrow for arrow in self.arrows if any(arrow.contains_node(node) for node in self.active_shape.nodes)]

                # Delete all arrows connected to the shape
                for arrow in arrows_to_delete:
                    arrow.deleteLater()
                    self.arrows.remove(arrow)

                self.active_shape = None
                return

            # Handle creation of arrow
            if self.active_shape.active_node:
                self.arrow_start = self.active_shape.active_node
                self.arrow_end = mouse_pos  # Set temporary end position
                return

            # Handle moving of shape
            if not self.active_shape.active_node:
                # Start moving the active shape
                self.drag_start = mouse_pos
                self.shape_start_pos = self.active_shape.pos()
                self.active_shape.locked = False
                self.active_shape.raise_()  # Bring the shape to the front
                self.shapes.remove(self.active_shape)  # Remove the shape from its current position
                self.shapes.append(self.active_shape)  # Add it back to the end of the list, so it's rendered last
                
        self.update()  # Trigger a repaint

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos()
            
        if self.active_shape and not self.active_shape.locked:
            # Move the active shape
            delta = mouse_pos - self.drag_start
            new_pos = self.shape_start_pos + delta
            self.active_shape.move(new_pos)
        elif self.arrow_start:
            # Update the temporary arrow's end position as the mouse moves
            self.arrow_end = mouse_pos

        # Update the active shape and node under the mouse
        self.active_shape = None  # Reset active shape
        for shape in self.shapes:
            if shape.geometry().contains(mouse_pos):
                self.active_shape = shape
                shape.has_active_node(mouse_pos)

        self.update()  # Trigger a repaint

    def mouseReleaseEvent(self, event):
        # Check if an arrow was being drawn
        if self.arrow_start and self.active_shape and self.active_shape.active_node:
            # Create an arrow between the two nodes if they are valid
            if self.active_shape.active_node != self.arrow_start:
                arrow = Arrow(self, self.arrow_start, self.active_shape.active_node)
                self.arrows.append(arrow)
                arrow.show()

        # Clear arrow and movement state after release
        self.arrow_start = None
        self.arrow_end = None
        if self.active_shape:
            self.drag_start = None
            self.shape_start_pos = None
            self.active_shape.locked = True
            
        self.update()  # Trigger repaint to clear the temporary arrow

    def paintEvent(self, event):
        with QPainter(self) as painter:
            pen = QPen(Qt.black, 2)
            painter.setPen(pen)
            
            # Draw the temporary arrow if it's being created
            if self.arrow_start and self.arrow_end:
                start_pos = self.arrow_start.get_global_position()
                painter.drawLine(start_pos, self.arrow_end)

            # Draw all the permanent arrows
            for arrow in self.arrows:
                arrow.update()  # Ensure arrows are drawn

    def mouseDoubleClickEvent(self, event):
        mouse_pos = event.pos()
        # Check if the mouse is over any arrows and remove them on double-click
        for arrow in self.arrows:
            if arrow.is_mouse_on_line(mouse_pos):
                self.arrows.remove(arrow)
                arrow.deleteLater()
                
    def save_to_json(self, file_path):
        shapes_data = []
        arrows_data = []
        
        # Convert shapes to simpler classes
        for shape in self.shapes:
            shape_data = ShapeData(
                shape_type=shape.__class__.__name__,  # Name of the class (Process, Decision, etc.)
                x=shape.pos().x(),
                y=shape.pos().y(),
                width=shape.width(),
                height=shape.height(),
                text=shape.text
            )
            shapes_data.append(shape_data)
        
        # Convert arrows to simpler classes
        for arrow in self.arrows:
            start_shape_index = self.shapes.index(arrow.start.parent)  # Shape index
            start_node_index = arrow.start.parent.nodes.index(arrow.start)  # Node index in shape
            end_shape_index = self.shapes.index(arrow.end.parent)
            end_node_index = arrow.end.parent.nodes.index(arrow.end)
            
            arrow_data = ArrowData(
                start_shape_index=start_shape_index,
                start_node_index=start_node_index,
                end_shape_index=end_shape_index,
                end_node_index=end_node_index
            )
            arrows_data.append(arrow_data)
        
        # Save shapes and arrows as JSON
        data = {
            "shapes": [shape.__dict__ for shape in shapes_data],
            "arrows": [arrow.__dict__ for arrow in arrows_data]
        }
        
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    
    def load_from_json(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        
        # Clear current shapes and arrows
        for shape in self.shapes:
            shape.deleteLater()
        for arrow in self.arrows:
            arrow.deleteLater()
        self.shapes.clear()
        self.arrows.clear()
        
        # Recreate shapes from data
        for shape_data in data['shapes']:
            shape_class = globals()[shape_data['shape_type']]  # Get the class by name (Process, Decision, etc.)
            new_shape = shape_class(self)
            new_shape.move(shape_data['x'], shape_data['y'])
            new_shape.resize(shape_data['width'], shape_data['height'])
            new_shape.text = shape_data['text']
            self.add_shape(new_shape)
        
        # Recreate arrows from data
        for arrow_data in data['arrows']:
            start_shape = self.shapes[arrow_data['start_shape_index']]
            start_node = start_shape.nodes[arrow_data['start_node_index']]
            end_shape = self.shapes[arrow_data['end_shape_index']]
            end_node = end_shape.nodes[arrow_data['end_node_index']]
            
            new_arrow = Arrow(self, start_node, end_node)
            self.arrows.append(new_arrow)
            new_arrow.show()
        
        self.update()
            
class Node:
    def __init__(self, parent: QWidget, qpoint: QPoint):
        self.parent = parent
        self.qpoint = qpoint
        
    def get_parent_position(self):
        return self.qpoint + QPoint(self.parent.width() // 2, self.parent.height() // 2)
    
    def get_global_position(self):
        return self.qpoint + QPoint(self.parent.width() // 2, self.parent.height() // 2) + self.parent.pos()

class Shape(QWidget):
    def __init__(self, parent: Window, width, height, node_positions: List[QPoint], node_radius: int):
        super().__init__(parent)
        self.locked = True
        self.active_node = None
        self.nodes = []
        self.text = "enter text"  # Variable to store the text for the shape
        self.node_radius = node_radius
        self.show_cross = False  # Flag to show or hide the cross
        self.cross_rect = QRect(1, 1, 10, 10)  # Define the cross area as a QRect

        for node_position in node_positions:
            self.nodes.append(Node(self, node_position))
        
        self.setFixedSize(width + node_radius * 2, height + node_radius * 2)
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Render cross if active
        if self.show_cross:
            with QPainter(self) as painter:
                pen = QPen(Qt.red, 2)
                painter.setPen(pen)
                # Draw cross at (0, 0)
                painter.drawLine(11, 1, 1, 11)
                painter.drawLine(1, 1, 11, 11)
        
        # Render the text in the center of the shape
        if self.text:
            with QPainter(self) as painter:
                painter.setPen(QPen(Qt.black, 2))
                painter.setFont(QtGui.QFont("Arial", 14))  # Adjust font if necessary
                text_rect = QRect(0, 0, self.width(), self.height())
                painter.drawText(text_rect, Qt.AlignCenter, self.text)
        
        # Render the nodes
        for node in self.nodes:
            with QPainter(self) as painter:
                painter.setPen(Qt.NoPen)
                if self.active_node == node:
                    painter.setBrush(QBrush(QColor(255, 255, 0)))
                else:
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(node.get_parent_position(), self.node_radius, self.node_radius)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Open an input dialog to ask for text
            text, ok = QInputDialog.getText(self, "Input Text", "Enter text for the shape:") # It looks so bad...
            if ok and text:
                self.text = text  # Set the shape's text
                self.update()  # Trigger a repaint to show the new text
    
    def leaveEvent(self, event):
        self.active_node = None
        self.show_cross = False
        self.update()
        
    def enterEvent(self, event):
        self.show_cross = True
        self.update()

    def has_active_node(self, mouse_pos):
        self.active_node = None
        for node in self.nodes:
            distance = math.hypot(mouse_pos.x() - node.get_global_position().x(), 
                                  mouse_pos.y() - node.get_global_position().y())
            if distance < self.node_radius:
                self.active_node = node
        return self.active_node

    def on_cross(self, mouse_pos):
        return self.cross_rect.contains(mouse_pos - self.pos())
        
class Decision(Shape):
    def __init__(self, parent):
        width = 130
        height = 130 
        node_positions = [
            QPoint(-65, 0),  # Left
            QPoint(65, 0),   # Right
            QPoint(0, 65),   # Bottom
            QPoint(0, -65)   # Top
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setPen(QPen(Qt.black, 2))
            center_x = self.width() // 2
            center_y = self.height() // 2
            # Draw a diamond shape
            points = [
                QPoint(center_x, center_y - 65),
                QPoint(center_x + 65, center_y),
                QPoint(center_x, center_y + 65),
                QPoint(center_x - 65, center_y) 
            ]
            painter.drawPolygon(QtGui.QPolygon(points))  # Diamond (Decision)
            
        super().paintEvent(event)  # Render the nodes

class Terminator(Shape):
    def __init__(self, parent):
        width = 130
        height = 80
        node_positions = [
            QPoint(-65, 0),
            QPoint(65, 0),  
            QPoint(0, 40),  
            QPoint(0, -40)
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setPen(QPen(Qt.black, 2))
            center_x = self.width() // 2
            center_y = self.height() // 2
            # Draw an oval (capsule) shape
            painter.drawRoundedRect(center_x - 65, center_y - 40, 130, 80, 40, 40)
            
        super().paintEvent(event)  # Render the nodes
   
class Process(Shape):
    def __init__(self, parent):
        width = 130
        height = 80
        node_positions = [
            QPoint(-65, 0),
            QPoint(65, 0),
            QPoint(0, 40),
            QPoint(0, -40)
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setPen(QPen(Qt.black, 2))
            center_x = self.width() // 2
            center_y = self.height() // 2
            # Draw a rectangle (Process)
            painter.drawRect(center_x - 65, center_y - 40, 130, 80)
            
        super().paintEvent(event)  # Render the nodes

class IO(Shape):
    def __init__(self, parent):
        width = 130
        height = 80
        # Adjust node positions to the middle of each side of the parallelogram
        node_positions = [
            QPoint(0, -40),
            QPoint(60, 0),
            QPoint(0, 40),
            QPoint(-60, 0)
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.setPen(QPen(Qt.black, 2))
            center_x = self.width() // 2
            center_y = self.height() // 2
            # Draw a parallelogram leaning the other way
            points = [
                QPoint(center_x - 55, center_y - 40),
                QPoint(center_x + 65, center_y - 40),
                QPoint(center_x + 55, center_y + 40),
                QPoint(center_x - 65, center_y + 40) 
            ]
            painter.drawPolygon(QtGui.QPolygon(points))
            
        super().paintEvent(event)  # Render the nodes

class Arrow(QWidget):
    def __init__(self, parent, start_position: Node, end_position: Node):
        super().__init__(parent)
        self.start = start_position
        self.end = end_position
        self.setFixedSize(parent.size())
        self.setAttribute(Qt.WA_TransparentForMouseEvents) 
        
    def paintEvent(self, event):
        with QPainter(self) as painter:
            pen = QtGui.QPen(QtGui.QColor('black'), 3)
            painter.setPen(pen)
            painter.drawLine(self.mapToParent(self.start.get_global_position()), self.end.get_global_position())
    
    def contains_node(self, node: Node) -> bool:
        return node == self.start or node == self.end        
    
    def is_mouse_on_line(self, mouse_pos: QPoint, threshold=5) -> bool:
        start_pos = self.start.get_global_position()
        end_pos = self.end.get_global_position()
        
        # Get coordinates for start, end, and mouse position
        x1, y1 = start_pos.x(), start_pos.y()
        x2, y2 = end_pos.x(), end_pos.y()
        mx, my = mouse_pos.x(), mouse_pos.y()

        # Calculate the distance from the mouse position to the line
        numerator = abs((x2 - x1) * (y1 - my) - (x1 - mx) * (y2 - y1))
        denominator = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        # If the line segment has zero length (edge case), return False
        if denominator == 0:
            return False
        distance = numerator / denominator
        
        # Check if the mouse is close enough to the line (within threshold)
        return distance <= threshold