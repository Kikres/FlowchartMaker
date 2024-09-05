from models.event_bus import EventBus
from modules.gui_module import FlowchartEditor

class FlowchartMaker:
    def __init__(self) -> None:
        self.__event_bus = EventBus()
        self.__flowchart_editor = FlowchartEditor(self.__event_bus)
        
    def start(self):
        self.__event_bus.emit("app:initalize")

def main():
    app = FlowchartMaker()
    app.start()

if __name__ == "__main__":
    main()