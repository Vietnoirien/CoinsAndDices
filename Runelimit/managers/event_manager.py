class EventManager:
    def __init__(self, game_table):
        self.game_table = game_table
        self.events = self.game_table.biome_manager.events
    
    def check_current_position(self):
        current_pos = self.game_table.get_player_position()
        if current_pos in self.events:
            event = self.events[current_pos]
            return self.trigger_event(event)
        return False
    
    def trigger_event(self, event):
        event_type = event["type"]
        event_description = event["description"]
        # Logique spécifique selon le type d'événement
        return True
