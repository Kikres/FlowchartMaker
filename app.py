from models.event_bus import EventBus
from modules.gui_module import FlowchartEditor
from PySide6 import QtWidgets
import sys

class FlowchartMaker:
    def __init__(self) -> None:
        self.__event_bus = EventBus()
        self.__flowchart_editor = FlowchartEditor(self.__event_bus)
        
    def start(self):
        # Initialize flowchart editor and emit event
        print("Initalize UI")
        self.__event_bus.emit("app:initialize")

def main():
    # Create the Qt application
    app = QtWidgets.QApplication(sys.argv)
    
    # Create the main application object
    flowchart_app = FlowchartMaker()
    
    # Start the flowchart application (this will emit the event)
    flowchart_app.start()
    
    # Run the Qt event loop (outside the event bus)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
