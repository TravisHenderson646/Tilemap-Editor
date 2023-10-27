'''
todo small:
- ability to rotate and flip images?
- say saved for a sec when you hit save
- use WITH statement for open and closing files

todo big:
- could zoom out by rendering tiles half size
- make tile groups clickable, maybe right clicking the group cycles its variant
- undo
- floodfill
- paralax the entire map could have a layer associated with it like a depth, such as 'player layer' 'first layer behind player', for 
'''

import sys
from math import floor

import pygame as pg

from scripts.image_loader import load_images
from scripts.tilemap import Tilemap
from scripts.button import Button

RENDER_SCALE = 4.0 #todo based on the screen

BLACK = pg.Color(0, 0, 0)


class Editor:
    def __init__(self):
        pg.init()

        pg.display.set_caption('Level Editor')
        pg.mouse.set_cursor(pg.cursors.broken_x)
        
        self.screen = pg.display.set_mode((1280, 720))
        self.display = pg.Surface((320,180))

        self.clock = pg.time.Clock()

        
        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'enemies': load_images('tiles/enemies'),
            'exits': load_images('tiles/exits'),
            'spawns': load_images('tiles/spawns'),
            'special': load_images('tiles/special'),
            'unlocks': load_images('tiles/unlocks'),
            'npcs': load_images('tiles/npcs'),
            }
        
        self.movement = [False, False, False, False]
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.tile_size = 8
        
        self.tilemap = Tilemap(self, tile_size=self.tile_size)
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
        
        
        self.scroll = pg.Vector2(0, 0)
        self.rounded_scroll = pg.Vector2(0, 0)
        self.tile_pos_rounded = (0, 0)
        self.mouse_pos: pg.Vector2()
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.grid_on = True
        
        ### Buttons
        self.is_drawn = True
        self.attackable = True
        self.tags = []
        self.grass_button = Button((5, 167, 10, 10), self.select_grass)
        self.grass_button.image = self.assets[self.tile_list[1]][0]
        self.dirt_button = Button((5, 141, 10, 10), self.select_dirt)
        self.dirt_button.image = self.assets[self.tile_list[6]][0]
        self.spike_button = Button((5, 128, 10, 10), self.select_spike)
        self.spike_button.image = self.assets[self.tile_list[6]][1]
        self.decor_button = Button((5, 154, 10, 10), self.select_decor)
        self.decor_button.image = self.assets[self.tile_list[0]][0]
        self.edit_tags_button = Button((307, 167, 10, 10), self.edit_tags)
        self.clear_tags_button = Button((307, 154, 10, 10), self.clear_tags)
    

    def select_decor(self):
        self.tile_group = 0
        self.tile_variant = 0
        self.tags = ['decor', 'rendered', 'breakable']
        print(f'grass: {self.tags}')
        
    def select_spike(self):
        self.tile_group = 6
        self.tile_variant = 1
        self.tags = ['spike', 'painted', 'attackable', 'clanker', 'solid', 'hitbox']
        print(f'grass: {self.tags}')
        
    def select_dirt(self):
        self.tile_group = 6
        self.tile_variant = 0
        self.tags = ['dirt', 'rendered', 'attackable', 'breakable', 'clanker', 'solid']
        print(f'grass: {self.tags}')
    
    def edit_tags(self):
        # List of keywords: drawn, solid, exit, entrance, north, south, east, west
        print('Type a str for new tile.tags:  ')
        print('painted chunked rendered solid attackable breakable clanker exit entrance north south east west')
        for tag in input('').split():
            self.tags.append(tag)
        print(self.tags)    
        
    def clear_tags(self):
        # List of keywords: drawn, solid, exit, entrance, north, south, east, west
        self.tags = []
        print(self.tags)

    def select_grass(self):
        self.tile_group = 1
        self.tile_variant = 0
        self.tags = ['painted', 'chunked']
        print(f'grass: {self.tags}')
        
    def select_attackable(self):
        self.tile_group = 4
        self.tile_variant = 0
        self.tags = ['rendered', 'attackable']
        print(f'{self.tags}')
                
    def floodfill(self, target_pos):
        target_key = f'{target_pos[0]};{target_pos[1]}'
        if target_key not in self.tilemap.tilemap.keys():
            self.tilemap.tilemap[target_key] = {
                'type': self.tile_list[self.tile_group],
                'variant': self.tile_variant,
                'pos': (floor(target_pos[0] * self.tile_size), floor(target_pos[1] * self.tile_size)),
                'tags': self.tags
            }
            self.floodfill((target_pos[0]    , target_pos[1] + 1))
            self.floodfill((target_pos[0]    , target_pos[1] - 1))
            self.floodfill((target_pos[0] + 1, target_pos[1]    ))
            self.floodfill((target_pos[0] - 1, target_pos[1]    ))
        
    def event_loop(self):
        self.mouse_pos = pg.Vector2(pg.mouse.get_pos()) // RENDER_SCALE
        #tile_pos should be tile_coord?
        tile_pos = (self.mouse_pos + self.rounded_scroll) / self.tilemap.tile_size
        self.tile_pos_rounded = (floor(tile_pos[0]), floor(tile_pos[1]))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clicking = True
                    if not self.grid_on:
                        self.tilemap.offgrid_tiles.append({
                            'type': self.tile_list[self.tile_group],
                            'variant': self.tile_variant,
                            'pos': (floor(self.mouse_pos[0] + self.rounded_scroll[0]), floor(self.mouse_pos[1] + self.rounded_scroll[1])),
                            'tags': self.tags,
                            })
                        print(self.tilemap.offgrid_tiles[-1])
                if event.button == 2:
                    self.grass_button.get_event(event, self.mouse_pos)
                    self.dirt_button.get_event(event, self.mouse_pos)
                    self.spike_button.get_event(event, self.mouse_pos)
                    self.decor_button.get_event(event, self.mouse_pos)
                    self.clear_tags_button.get_event(event, self.mouse_pos)
                    self.edit_tags_button.get_event(event, self.mouse_pos)
                    tile_hovered = str(self.tile_pos_rounded[0]) + ';' + str(self.tile_pos_rounded[1])
                    if tile_hovered in self.tilemap.tilemap:
                        print(self.tilemap.tilemap[tile_hovered])
                        print(tile_hovered)
                    for tile in self.tilemap.offgrid_tiles.copy():
                        tile_image = self.assets[tile['type']][tile['variant']]
                        tile_rect = pg.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_image.get_width(), tile_image.get_height())
                        if tile_rect.collidepoint(self.mouse_pos):
                            print(tile)
                if event.button == 3:
                    self.right_clicking = True
                if self.shift:
                    if event.button == 4:
                        self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    if event.button == 5:
                        self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                else:
                    if event.button == 4:
                        self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                        self.tile_variant = 0
                    if event.button == 5:
                        self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                        self.tile_variant = 0
                        
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.clicking = False
                if event.button == 3:
                    self.right_clicking = False
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                if event.key == pg.K_a:
                    self.movement[0] = True
                if event.key == pg.K_d:
                    self.movement[1] = True
                if event.key == pg.K_w:
                    self.movement[2] = True
                if event.key == pg.K_s:
                    self.movement[3] = True
                if event.key == pg.K_g:
                    self.grid_on = not self.grid_on
                if event.key == pg.K_t:
                    self.tilemap.autotile()
                if event.key == pg.K_l:
                    self.floodfill(self.tile_pos_rounded)
                if event.key == pg.K_RETURN:
                    self.tilemap.save('map.json')
                if event.key == pg.K_LSHIFT:
                    self.shift = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_a:
                    self.movement[0] = False
                if event.key == pg.K_d:
                    self.movement[1] = False
                if event.key == pg.K_w:
                    self.movement[2] = False
                if event.key == pg.K_s:
                    self.movement[3] = False
                if event.key == pg.K_LSHIFT:
                    self.shift = False
        

    def update(self):        
        self.scroll[0] += (self.movement[1] - self.movement[0]) * 3
        self.scroll[1] += (self.movement[3] - self.movement[2]) * 3
        
        self.rounded_scroll = pg.Vector2((floor(self.scroll[0]), floor(self.scroll[1])))
        
        if self.clicking and self.grid_on:
            tile_clicked = str(self.tile_pos_rounded[0]) + ';' + str(self.tile_pos_rounded[1])
            self.tilemap.tilemap[tile_clicked] = {
                'type': self.tile_list[self.tile_group],
                'variant': self.tile_variant,
                'pos': (floor(self.tile_pos_rounded[0] * self.tile_size), floor(self.tile_pos_rounded[1] * self.tile_size)),
                'tags': self.tags
                }
            print(self.tilemap.tilemap[tile_clicked])
        if self.right_clicking:
            tile_hovered = str(self.tile_pos_rounded[0]) + ';' + str(self.tile_pos_rounded[1])
            if tile_hovered in self.tilemap.tilemap:
                del self.tilemap.tilemap[tile_hovered]
            for tile in self.tilemap.offgrid_tiles.copy():
                tile_image = self.assets[tile['type']][tile['variant']]
                tile_rect = pg.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_image.get_width(), tile_image.get_height())
                if tile_rect.collidepoint(self.mouse_pos):
                    self.tilemap.offgrid_tiles.remove(tile)

    def render(self):
        self.display.fill((0, 0, 0, 0))
        current_tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
        self.tilemap.render(self.display, offset=self.rounded_scroll)
        
        #tile_pos should be tile_coord?
        if self.grid_on:
            self.display.blit(current_tile_image, (self.tile_pos_rounded[0] * self.tilemap.tile_size - self.rounded_scroll[0], self.tile_pos_rounded[1] * self.tilemap.tile_size - self.rounded_scroll[1]))
        else:
            self.display.blit(current_tile_image, (self.mouse_pos))

        #current selected in top left
        self.display.blit(current_tile_image, (0, 0))
        
        # render the buttons
        self.grass_button.render(self.display)
        self.dirt_button.render(self.display)
        self.spike_button.render(self.display)
        self.decor_button.render(self.display)
        self.edit_tags_button.render(self.display)
        self.clear_tags_button.render(self.display)
        
        self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (0,0))
        pg.display.update()
        self.clock.tick(60)

    def run(self):
        while True:
            self.event_loop()
            self.update()
            self.render()
        

Editor().run()
