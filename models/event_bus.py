class EventBus:
    def __init__(self) -> None:
        self.__listeners = {}
        
    # Register event
    def on(self, event: str, listener) -> None:
        if event not in self.__listeners:
            self.__listeners[event] = []
        self.__listeners[event].append(listener)
        
    # Emit event
    def emit(self, event: str, data = None):
        if event in self.__listeners:
            for listener in self.__listeners[event]:
                listener(data)