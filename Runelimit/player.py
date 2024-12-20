import json
import os
from pathlib import Path

class Player:
    def __init__(self, character_file, starting_position=(0, 0)):
        self.character_data = self.load_character(character_file)
        self.name = self.character_data["name"]
        self.player_name = self.name  # Nouveau : stockage du nom du joueur
        self.level = self.character_data["level"]
        self.exp = self.character_data["exp"]
        self.gold = self.character_data["gold"]
        self.pv = self.character_data["pv"]
        self.fatigue = self.character_data["fatigue"]
        self.distance = self.character_data["distance"]
        self.distance_degat = self.character_data["distance_degat"]
        self.melee = self.character_data["melee"]
        self.melee_degat = self.character_data["melee_degat"]
        self.magie = self.character_data["magie"]
        self.magie_degat = self.character_data["magie_degat"]
        
        # Position sur la grille
        self.position = starting_position
        self.biomes = self.load_biomes()        
    @staticmethod
    def load_character(character_file):
        with open(character_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def load_biomes():
        current_dir = Path(__file__).parent
        biomes_path = current_dir / 'biomes.json'
        with open(biomes_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @staticmethod
    def get_available_characters():
        current_dir = Path(__file__).parent
        characters_dir = current_dir / 'characters'
        return list(characters_dir.glob("*.json"))
    
    def move_to(self, new_position):
        if str(new_position) in self.biomes:
            self.position = new_position
            return True
        return False
    
    def get_current_biome(self):
        return self.biomes.get(str(self.position))
    
    def level_up(self):
        self.level += 1
        
    def gain_exp(self, amount):
        self.exp += amount
        
    def gain_gold(self, amount):
        self.gold += amount
        
    def take_damage(self, amount):
        self.pv -= amount
        return self.pv <= 0
        
    def heal(self, amount):
        self.pv += amount
        
    def add_fatigue(self, amount):
        self.fatigue += amount
        
    def remove_fatigue(self, amount):
        self.fatigue -= amount