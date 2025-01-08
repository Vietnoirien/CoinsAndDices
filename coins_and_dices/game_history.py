class GameHistory:
    _instance = None
    _history = []
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GameHistory()
        return cls._instance
    
    def add_event(self, event):
        self._history.append(event)
    
    def get_history(self):
        return self._history
