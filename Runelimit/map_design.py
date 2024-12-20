import wx

def get_biomes():
    return {
        "Marais": {"primary": wx.Colour(0, 100, 100), "pattern": None},
        "Plaine": {"primary": wx.Colour(144, 238, 144), "pattern": None},
        "Riviere": {
            "primary": wx.Colour(144, 238, 144),
            "pattern": {"color": wx.Colour(0, 0, 255), "type": "line"}
        },
        "Colline": {"primary": wx.Colour(165, 113, 78), "pattern": None},
        "Route": {
            "primary": wx.Colour(144, 238, 144),
            "pattern": {"color": wx.Colour(139, 69, 19), "type": "line"}
        },
        "Montagne": {"primary": wx.Colour(101, 67, 33), "pattern": None},
        "Ville": {"primary": wx.Colour(128, 128, 128), "pattern": None},
        "Foret": {"primary": wx.Colour(0, 100, 0), "pattern": None}
    }

def should_connect(biome1, biome2):
    if not biome1 or not biome2:
        return False
        
    if biome1 == "Riviere" and biome2 in ["Riviere", "Ville", "Marais"]:
        return True
    
    if biome1 == "Route" and biome2 in ["Route", "Ville"]:
        return True
    
    return False

def find_river_connections(hex_biomes, col, row, get_adjacent_hexes):
    marsh_neighbors = []
    other_water_neighbors = []

    for adj_col, adj_row in get_adjacent_hexes(col, row):
        adj_biome = hex_biomes.get(str((adj_col, adj_row)))
        if adj_biome == "Marais":
            marsh_neighbors.append((adj_col, adj_row))
        elif adj_biome in ["Riviere", "Ville"]:
            other_water_neighbors.append((adj_col, adj_row))

    connections = []
    connections.extend(marsh_neighbors)
    
    remaining_slots = 2 - len(connections)
    if remaining_slots > 0:
        connections.extend(other_water_neighbors[:remaining_slots])

    return connections[:2]
