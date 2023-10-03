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
'''

import sys
from math import floor

import pygame as pg

from scripts.image_loader import load_images
from scripts.tilemap import Tilemap
from scripts.button import Button

RENDER_SCALE = 2.0 #todo based on the screen


class Editor:
    def __init__(self):
        pg.init()

        pg.display.set_caption('Level Editor')
        pg.mouse.set_cursor(pg.cursors.broken_x)
        
        self.screen = pg.display.set_mode((1280, 720))
        self.display = pg.Surface((640,360))

        self.clock = pg.time.Clock()

        
        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
            'loading_zones': load_images('tiles/loading_zones'),
            }
        
        self.movement = [False, False, False, False]
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        
        self.tilemap = Tilemap(self, tile_size=32)
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
        
        
        self.scroll = pg.Vector2(0, 0)
        self.rounded_scroll = pg.Vector2(0, 0)
        self.tile_pos_rounded = (0, 0)
        self.mouse_pos: pg.Vector2()
        
        self.tile_list = list(self.assets)
        self.tile_group = 0 # I think this should be tile_type
        self.tile_variant = 0
        self.grid_on = True
        
        self.keep = True
        self.keep_button = Button((10, 600, 25, 25), self.test)

    def test(self):
        self.keep = not self.keep
        print(f'wtf is going on{self.keep}')
        
    def event_loop(self):
        self.mouse_pos = pg.Vector2(pg.mouse.get_pos()) / RENDER_SCALE
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
                    self.keep_button.get_event(event)
                    if not self.grid_on:
                        # maybe should round the mouse pos for this
                        tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
                        self.tilemap.offgrid_tiles.append({
                            'type': self.tile_list[self.tile_group],
                            'variant': self.tile_variant,
                            'pos': (self.mouse_pos[0] + self.scroll[0], self.mouse_pos[1] + self.scroll[1]),
                        #    'rect': pg.Rect(self.mouse_pos[0] + self.scroll[0], self.mouse_pos[1] + self.scroll[1], tile_image.get_width(), tile_image.get_height())
                            })
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
        

            

        # this should probably go after the event queue
        if self.clicking and self.grid_on:
            tile_clicked = str(self.tile_pos_rounded[0]) + ';' + str(self.tile_pos_rounded[1])
            self.tilemap.tilemap[tile_clicked] = {
                'type': self.tile_list[self.tile_group],
                'variant': self.tile_variant,
                'pos': self.tile_pos_rounded,
                #   'rect': pg.Rect(self.tile_pos_rounded[0] * self.tilemap.tile_size, self.tile_pos_rounded[1] * self.tilemap.tile_size, self.tilemap.tile_size, self.tilemap.tile_size)
                }
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
        self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (0,0))
        
        self.keep_button.render(self.screen)
        
        pg.display.update()
        self.clock.tick(60)

    def run(self):
        while True:
            self.event_loop()
            self.update()
            self.render()
        

Editor().run()
