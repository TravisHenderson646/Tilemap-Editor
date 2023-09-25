from math import floor
import json

import pygame as pg

NEIGHBOR_OFFSET = [(a, b) for a in [-1, 0, 1] for b in [-1, 0, 1]]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (0, 1), (-1, 0), (0, -1)])): 8,
}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
          
    def save(self, path):
        file = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, file, indent=2)
        file.close()
        
    def load(self, path):
        file = open(path, 'r')
        map_data = json.load(file)
        file.close()
        
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        
    def autotile(self):
        for loc, tile in self.tilemap.items():
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset):
        '''Takes the display surface and screen scroll and renders the tilemap section'''
        #have to optimize offgrid tiles at some point probably once i have enough
        for tile in self.offgrid_tiles: #todo: dafluffy says this order but maybe its cooler to have offgrin in front THINK ABOUT IT
            surf.blit(self.game.assets[tile['type']][tile['variant']], (floor(tile['pos'][0] - offset[0]), floor(tile['pos'][1] - offset[1])))

        for x in range(floor(offset[0] // self.tile_size), floor((offset[0] + surf.get_width()) // self.tile_size + 1)):
            for y in range(floor(offset[1] // self.tile_size), floor((offset[1] + surf.get_height()) // self.tile_size + 1)):
                loc = str(x) +';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]

                    surf.blit(self.game.assets[tile['type']][tile['variant']], (floor(tile['pos'][0]) * self.tile_size - offset[0], floor(tile['pos'][1]) * self.tile_size - offset[1]))
                    
                    
                    
                    