


# class FlowchartShape(QWidget):
#     def __init__(self, configuration: ShapeConfiguration, parent=None):
#         super().__init__(parent)
#         self.nodes = configuration.nodes     
#         self.locked_state = False
#         self.shape_width = configuration.width  # Shape width
#         self.shape_height = configuration.height  # Shape height
#         padding = 40 
#         self.setFixedSize(self.shape_width + padding, self.shape_height + padding)  # Padding to prevent cut-off
#         self.setMouseTracking(True)

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.locked_state = True
#             self.drag_start = event.pos()

#     def mouseMoveEvent(self, event):
#         # Handle dragging of the widget
#         if self.locked_state:
#             self.move(self.mapToParent(event.pos() - self.drag_start))

#         # Update node hover detection
#         mouse_pos = event.pos()
#         node_hovered = False
#         for i, node in enumerate(self.get_centered_node_positions()):
#             if math.hypot(mouse_pos.x() - node.x(), mouse_pos.y() - node.y()) < 15:
#                 self.selected_node = i
#                 node_hovered = True
#                 break
#         if not node_hovered:
#             self.selected_node = None

#         self.update()

#     def mouseReleaseEvent(self, event):
#         print("Mouse released", self.selected_node)
#         self.locked_state = False
        
#     def leaveEvent(self, event):
#         self.update()
        
# class Arrow(QWidget):
#     def __init__(self, parent, noda_a: Node, node_b: Node):
#         super().__init__(parent)
#         self. 
#         # Set the widget to be transparent to mouse events
#         self.setAttribute(Qt.WA_TransparentForMouseEvents)
#         self.setFixedSize(parent.size())

          
#     def paintEvent(self, event):
#         with QPainter(self) as painter:
#             pen = QPen(Qt.black, 2)
#             painter.setPen(pen) 
#             # Draw the line relative to the widget's own coordinates
#             a_center = self.shape_a.get_center()
#             b_center = self.shape_b.get_center()  
#             painter.drawLine(a_center, b_center)
#             self.setFixedSize(abs(a_center.x() + b_center.x()), abs(a_center.y() + b_center.y()))
#         self.update()
        








# class FlowchartShape(QWidget):
#     def __init__(self, configuration: ShapeConfiguration, parent=None):
#         super().__init__(parent)
#         self.nodes = configuration.nodes
        
        
#         self.selected_node = None
#         self.locked_state = False
#         self.shape_width = configuration.width  # Shape width
#         self.shape_height = configuration.height  # Shape height
#         padding = 40
        
#         self.setFixedSize(self.shape_width + padding, self.shape_height + padding)  # Padding to prevent cut-off
#         self.setMouseTracking(True)
    
#     def get_center(self):
#         return QPoint(self.x() + (self.width() // 2), self.y() + (self.height() // 2))

#     def get_centered_node_positions(self):
#         # Calculate the center of the widget (window)
#         center_x = self.width() // 2
#         center_y = self.height() // 2
#         # Adjust the node positions relative to the shape's center
#         centered_nodes = [QPoint(center_x + node.x(), center_y + node.y()) for node in self.nodes]
#         return centered_nodes

#     def paintEvent(self, event):
#         self.draw_nodes()

#     def draw_nodes(self):
#         with QPainter(self) as painter:
#             painter.setPen(Qt.NoPen)
#             centered_nodes = self.get_centered_node_positions()

#             for i, node in enumerate(centered_nodes):
#                 if self.selected_node == i:
#                     painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red when close
#                 else:
#                     painter.setBrush(Qt.BrushStyle.NoBrush)
#                 painter.drawEllipse(node, 8, 8)  # Drawing node circles

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.locked_state = True
#             self.drag_start = event.pos()

#     def mouseMoveEvent(self, event):
#         # Handle dragging of the widget
#         if self.locked_state:
#             self.move(self.mapToParent(event.pos() - self.drag_start))

#         # Update node hover detection
#         mouse_pos = event.pos()
#         node_hovered = False
#         for i, node in enumerate(self.get_centered_node_positions()):
#             if math.hypot(mouse_pos.x() - node.x(), mouse_pos.y() - node.y()) < 15:
#                 self.selected_node = i
#                 node_hovered = True
#                 break
#         if not node_hovered:
#             self.selected_node = None

#         self.update()

#     def mouseReleaseEvent(self, event):
#         print("Mouse released", self.selected_node)
#         self.locked_state = False
        
#     def leaveEvent(self, event):
#         self.update()
        
# class Arrow(QWidget):
#     def __init__(self, parent):
#         super().__init__(parent)
#         # Set the widget to be transparent to mouse events
#         self.setAttribute(Qt.WA_TransparentForMouseEvents)
#         self.setFixedSize(parent.size())

          
#     def paintEvent(self, event):
#         with QPainter(self) as painter:
#             pen = QPen(Qt.black, 2)
#             painter.setPen(pen) 
#             # Draw the line relative to the widget's own coordinates
#             a_center = self.shape_a.get_center()
#             b_center = self.shape_b.get_center()  
#             painter.drawLine(a_center, b_center)
#             self.setFixedSize(abs(a_center.x() + b_center.x()), abs(a_center.y() + b_center.y()))
#         self.update()
#         self.shape_a.update()
#         self.shape_b.update()

# ## Group Widget ###

# class GroupWidget(QWidget):
#     def __init__(self, parent, shape_a: FlowchartShape, shape_b: FlowchartShape):
#         super().__init__(parent)
#         self.shape_a = shape_a
#         self.shape_b = shape_b
#         # Set the widget to be transparent to mouse events
#         self.setAttribute(Qt.WA_TransparentForMouseEvents)
#         self.setFixedSize(parent.size())

          
#     def paintEvent(self, event):
#         with QPainter(self) as painter:
#             pen = QPen(Qt.black, 2)
#             painter.setPen(pen) 
#             # Draw the line relative to the widget's own coordinates
#             a_center = self.shape_a.get_center()
#             b_center = self.shape_b.get_center()  
#             painter.drawLine(a_center, b_center)
#             self.setFixedSize(abs(a_center.x() + b_center.x()), abs(a_center.y() + b_center.y()))
#         self.update()
#         self.shape_a.update()
#         self.shape_b.update()