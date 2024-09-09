import sys
import json
import math
from dataclasses import dataclass
from typing import List
from PySide6 import QtCore, QtWidgets, QtGui

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
    
@dataclass
class DiagramData:
    shapes: List[ShapeData]
    arrows: List[ArrowData]

class FlowchartEditor:
    def __init__(self):
        self.window = None
        self.run()

    def run(self):
        self.window = Window(self)
        self.window.setWindowTitle("Flowchart Proof of Concept")
        self.window.show()

    def handle_save(self, diagram_data: DiagramData):
        # Ask the user for the save file path
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self.window, "Save Flowchart", "", "JSON Files (*.json);;All Files (*)")

        if file_path:
            with open(file_path, "w") as file:
                json.dump(diagram_data.__dict__, file, default=lambda o: o.__dict__, indent=4)
            print(f"Flowchart saved to {file_path}")

    def handle_load(self) -> DiagramData:
        # Ask the user for the load file path
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self.window, "Load Flowchart", "", "JSON Files (*.json);;All Files (*)")

        if file_path:
            with open(file_path, "r") as file:
                data = json.load(file)

            diagram_data = DiagramData(
                shapes=[ShapeData(**shape_data) for shape_data in data['shapes']],
                arrows=[ArrowData(**arrow_data) for arrow_data in data['arrows']]
            )
            print(f"Flowchart loaded from {file_path}")
            return diagram_data
        return None  # Return None if no file is selected

class Window(QtWidgets.QMainWindow):
    def __init__(self, editor: FlowchartEditor):
        super().__init__()
        self.editor = editor  # Store reference to FlowchartEditor
        self.setWindowTitle("Flowchart Creator")
        self.setGeometry(100, 100, 1000, 600)  # Initial window size

        # Set the main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QHBoxLayout(central_widget)

        # Create the flowchart area and toolbar
        self.flowchart_area = Area(self)
        self.toolbar = Toolbar(self)

        # Add flowchart area to the left and toolbar to the right
        layout.addWidget(self.flowchart_area, stretch=5)
        layout.addWidget(self.toolbar, stretch=1)

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
        diagram_data = self.flowchart_area.save_to_diagram_data()
        self.editor.handle_save(diagram_data)

    def handle_load(self):
        diagram_data = self.editor.handle_load()
        self.flowchart_area.load_from_diagram_data(diagram_data)

class Toolbar(QtWidgets.QWidget):
    def __init__(self, parent: Window):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # Add buttons for shapes
        btn_add_process = QtWidgets.QPushButton("Add Process", self)
        btn_add_decision = QtWidgets.QPushButton("Add Decision", self)
        btn_add_terminator = QtWidgets.QPushButton("Add Terminator", self)
        btn_add_io = QtWidgets.QPushButton("Add I/O", self)

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
        btn_save = QtWidgets.QPushButton("Save", self)
        btn_load = QtWidgets.QPushButton("Load", self)
        
        btn_save.clicked.connect(self.parent().handle_save)
        btn_load.clicked.connect(self.parent().handle_load)

        layout.addWidget(btn_save)
        layout.addWidget(btn_load)

class Area(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arrow_start = None
        self.arrow_end = None
        self.shapes = []
        self.arrows = []
        self.active_shape = None
        self.setMouseTracking(True)
    
    def add_shape(self, shape: QtWidgets.QWidget):
        shape.move(self.width() // 2 - shape.width() // 2, self.height() // 2 - shape.height() // 2)  # Center the shape on area
        self.shapes.append(shape)
        shape.show()
        self.update()  # Trigger repaint
    
    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
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
                self.drag_start = mouse_pos
                self.shape_start_pos = self.active_shape.pos()
                self.active_shape.locked = False
                self.active_shape.raise_()  # Bring the shape to the front
                self.shapes.remove(self.active_shape)
                self.shapes.append(self.active_shape)
                
        self.update()
        
    def mouseDoubleClickEvent(self, event):
        # Handle removal of arrows on double-click
        mouse_pos = event.pos()
        arrows_to_remove = []

        # Check if the mouse is over any arrows
        for arrow in self.arrows:
            if arrow.is_mouse_on_line(mouse_pos):
                arrows_to_remove.append(arrow)

        # Remove the arrows
        for arrow in arrows_to_remove:
            self.arrows.remove(arrow)
            arrow.deleteLater()

        self.update()  # Trigger a repaint after removal

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos()
            
        # Handle moving of shape or creation of arrow
        if self.active_shape and not self.active_shape.locked:
            delta = mouse_pos - self.drag_start
            new_pos = self.shape_start_pos + delta
            self.active_shape.move(new_pos)
        elif self.arrow_start:
            self.arrow_end = mouse_pos

        # Handle hovering over nodes
        self.active_shape = None
        for shape in self.shapes:
            if shape.geometry().contains(mouse_pos):
                self.active_shape = shape
                shape.has_active_node(mouse_pos)

        self.update()  # Trigger a repaint

    def mouseReleaseEvent(self, event):
        # Handle creation of arrow between two nodes
        if self.arrow_start and self.active_shape and self.active_shape.active_node:
            if self.active_shape.active_node != self.arrow_start:
                arrow = Arrow(self, self.arrow_start, self.active_shape.active_node)
                self.arrows.append(arrow)
                arrow.show()

        # Reset arrow and shape states
        self.arrow_start = None
        self.arrow_end = None
        if self.active_shape:
            self.drag_start = None
            self.shape_start_pos = None
            self.active_shape.locked = True
            
        self.update()

    def paintEvent(self, event):
        # Render arrows
        with QtGui.QPainter(self) as painter:
            pen = QtGui.QPen(QtCore.Qt.black, 2)
            painter.setPen(pen)
            
            if self.arrow_start and self.arrow_end:
                start_pos = self.arrow_start.get_global_position()
                painter.drawLine(start_pos, self.arrow_end)

            for arrow in self.arrows:
                arrow.update()

    def save_to_diagram_data(self) -> DiagramData:
        shapes_data = []
        arrows_data = []
        
        # Collect data for shapes
        for shape in self.shapes:
            shape_data = ShapeData(
                shape_type=shape.__class__.__name__,
                x=shape.pos().x(),
                y=shape.pos().y(),
                width=shape.width(),
                height=shape.height(),
                text=shape.text
            )
            shapes_data.append(shape_data)
        
        # Collect data for arrows
        for arrow in self.arrows:
            start_shape_index = self.shapes.index(arrow.start.parent)
            start_node_index = arrow.start.parent.nodes.index(arrow.start)
            end_shape_index = self.shapes.index(arrow.end.parent)
            end_node_index = arrow.end.parent.nodes.index(arrow.end)
            
            arrow_data = ArrowData(
                start_shape_index=start_shape_index,
                start_node_index=start_node_index,
                end_shape_index=end_shape_index,
                end_node_index=end_node_index
            )
            arrows_data.append(arrow_data)
        
        return DiagramData(shapes=shapes_data, arrows=arrows_data)
    
    def load_from_diagram_data(self, diagram_data: DiagramData):
        # Clear existing shapes and arrows
        for shape in self.shapes:
            shape.deleteLater()
        for arrow in self.arrows:
            arrow.deleteLater()
        self.shapes.clear()
        self.arrows.clear()
        
        # Create shapes from diagram data
        for shape_data in diagram_data.shapes:
            shape_class = globals()[shape_data.shape_type]
            new_shape = shape_class(self)
            self.add_shape(new_shape)
            new_shape.move(shape_data.x, shape_data.y)
            new_shape.resize(shape_data.width, shape_data.height)
            new_shape.text = shape_data.text
        
        # Create arrows from diagram data
        for arrow_data in diagram_data.arrows:
            start_shape = self.shapes[arrow_data.start_shape_index]
            start_node = start_shape.nodes[arrow_data.start_node_index]
            end_shape = self.shapes[arrow_data.end_shape_index]
            end_node = end_shape.nodes[arrow_data.end_node_index]
            
            new_arrow = Arrow(self, start_node, end_node)
            self.arrows.append(new_arrow)
            new_arrow.show()
        
        self.update() # Needs re-rendering

class Node:
    def __init__(self, parent: QtWidgets.QWidget, qpoint: QtCore.QPoint):
        self.parent = parent
        self.qpoint = qpoint
        
    def get_parent_position(self):
        return self.qpoint + QtCore.QPoint(self.parent.width() // 2, self.parent.height() // 2)
    
    def get_global_position(self):
        return self.qpoint + QtCore.QPoint(self.parent.width() // 2, self.parent.height() // 2) + self.parent.pos()

class Shape(QtWidgets.QWidget):
    def __init__(self, parent: Window, width, height, node_positions: List[QtCore.QPoint], node_radius: int):
        super().__init__(parent)
        self.locked = True
        self.active_node = None
        self.nodes = []
        self.text = "enter text"
        self.node_radius = node_radius
        self.show_cross = False
        self.cross_rect = QtCore.QRect(1, 1, 10, 10)  # Define the cross area as a QRect

        for node_position in node_positions:
            self.nodes.append(Node(self, node_position))
        
        self.setFixedSize(width + node_radius * 2, height + node_radius * 2)
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        # Render cross if active
        if self.show_cross:
            with QtGui.QPainter(self) as painter:
                pen = QtGui.QPen(QtCore.Qt.red, 2)
                painter.setPen(pen)
                # Use cross_rect to draw the cross
                painter.drawLine(self.cross_rect.topLeft(), self.cross_rect.bottomRight())
                painter.drawLine(self.cross_rect.topRight(), self.cross_rect.bottomLeft())
        
        # Render the text in the center of the shape
        if self.text:
            with QtGui.QPainter(self) as painter:
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
                painter.setFont(QtGui.QFont("Arial", 14))  # Adjust font if necessary
                text_rect = QtCore.QRect(0, 0, self.width(), self.height())
                painter.drawText(text_rect, QtCore.Qt.AlignCenter, self.text)
        
        # Render the nodes
        for node in self.nodes:
            with QtGui.QPainter(self) as painter:
                painter.setPen(QtCore.Qt.NoPen)
                if self.active_node == node:
                    painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
                else:
                    painter.setBrush(QtCore.Qt.NoBrush)
                painter.drawEllipse(node.get_parent_position(), self.node_radius, self.node_radius)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Set the shape's text, looks bad but works
            text, ok = QtWidgets.QInputDialog.getText(self, "Input Text", "Enter text for the shape:")
            if ok and text:
                self.text = text
                self.update()
    
    def leaveEvent(self, event):
        # Reset the active node and hide the cross when the mouse leaves the shape
        self.active_node = None
        self.show_cross = False
        self.update()
        
    def enterEvent(self, event):
        # Show the cross when the mouse enters the shape
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
            QtCore.QPoint(-65, 0),  # Left
            QtCore.QPoint(65, 0),   # Right
            QtCore.QPoint(0, 65),   # Bottom
            QtCore.QPoint(0, -65)   # Top
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QtGui.QPainter(self) as painter:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtGui.QColor(255, 255, 255))
            center_x = self.width() // 2
            center_y = self.height() // 2
            # Draw a diamond shape
            points = [
                QtCore.QPoint(center_x, center_y - 65),
                QtCore.QPoint(center_x + 65, center_y),
                QtCore.QPoint(center_x, center_y + 65),
                QtCore.QPoint(center_x - 65, center_y) 
            ]
            painter.drawPolygon(QtGui.QPolygon(points))  # Diamond (Decision)
            
        super().paintEvent(event)  # Render the nodes

class Terminator(Shape):
    def __init__(self, parent):
        width = 130
        height = 80
        node_positions = [
            QtCore.QPoint(-65, 0),
            QtCore.QPoint(65, 0),  
            QtCore.QPoint(0, 40),  
            QtCore.QPoint(0, -40)
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QtGui.QPainter(self) as painter:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtGui.QColor(255, 255, 255))
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
            QtCore.QPoint(-65, 0),
            QtCore.QPoint(65, 0),
            QtCore.QPoint(0, 40),
            QtCore.QPoint(0, -40)
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QtGui.QPainter(self) as painter:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtGui.QColor(255, 255, 255))
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
            QtCore.QPoint(0, -40),
            QtCore.QPoint(60, 0),
            QtCore.QPoint(0, 40),
            QtCore.QPoint(-60, 0)
        ]
        node_radius = 8
        super().__init__(parent, width, height, node_positions, node_radius)

    def paintEvent(self, event):
        with QtGui.QPainter(self) as painter:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtGui.QColor(255, 255, 255))
            center_x = self.width() // 2
            center_y = self.height() // 2
            # Draw a parallelogram leaning the other way
            points = [
                QtCore.QPoint(center_x - 55, center_y - 40),
                QtCore.QPoint(center_x + 65, center_y - 40),
                QtCore.QPoint(center_x + 55, center_y + 40),
                QtCore.QPoint(center_x - 65, center_y + 40) 
            ]
            painter.drawPolygon(QtGui.QPolygon(points))
            
        super().paintEvent(event)  # Render the nodes

class Arrow(QtWidgets.QWidget):
    def __init__(self, parent, start_position: Node, end_position: Node):
        super().__init__(parent)
        self.start = start_position
        self.end = end_position
        self.setFixedSize(parent.size())
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents) 
        
    def paintEvent(self, event):
        with QtGui.QPainter(self) as painter:
            pen = QtGui.QPen(QtGui.QColor('black'), 3)
            painter.setPen(pen)
            
            # Get the positions of the start and end points
            start_pos = self.mapToParent(self.start.get_global_position())
            end_pos = self.end.get_global_position()
    
            # Draw the main line
            painter.drawLine(start_pos, end_pos)
    
            # Calculate the direction vector of the line
            direction = QtCore.QLineF(start_pos, end_pos)
            angle = math.atan2(end_pos.y() - start_pos.y(), end_pos.x() - start_pos.x())  # Get the angle in radians
    
            # Length of the arrowhead lines
            arrow_size = 15
    
            # Calculate the arrowhead points using math.sin and math.cos
            left_arrowhead = QtCore.QPointF(
                end_pos.x() - arrow_size * math.cos(angle + math.radians(30)),
                end_pos.y() - arrow_size * math.sin(angle + math.radians(30))
            )
            right_arrowhead = QtCore.QPointF(
                end_pos.x() - arrow_size * math.cos(angle - math.radians(30)),
                end_pos.y() - arrow_size * math.sin(angle - math.radians(30))
            )
    
            # Draw the arrowhead using two lines that meet at the endpoint
            painter.drawLine(end_pos, left_arrowhead)
            painter.drawLine(end_pos, right_arrowhead)

    def contains_node(self, node: Node) -> bool:
        return node == self.start or node == self.end        
    
    def is_mouse_on_line(self, mouse_pos: QtCore.QPoint, threshold=5) -> bool:
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

if __name__ == "__main__":
    # Create the Qt application
    app = QtWidgets.QApplication(sys.argv)
    
    # Create the main application object (which will automatically start the flowchart editor)
    flowchart_editor = FlowchartEditor()
    
    # Run the Qt event loop
    sys.exit(app.exec())