'''
todo: make seperate files for Tilemap and utility that are just for this editor

todo: ability to rotate and flip images?

todo: say saved for a sec when you hit save
'''

import sys
from math import floor

import pygame as pg

from code.utility import load_images
from code.tilemap import Tilemap

RENDER_SCALE = 3.0 #todo based on the screen


class Editor:
    def __init__(self):
        pg.init()

        pg.display.set_caption('Level Editor')
        self.screen = pg.display.set_mode((960, 720))
        self.display = pg.Surface((320,240))

        self.clock = pg.time.Clock()

        
        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
            }
        
        self.movement = [False, False, False, False]
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
        
        
        self.scroll = pg.Vector2(0, 0)
        self.rounded_scroll = pg.Vector2(0, 0)
        
        self.tile_list = list(self.assets)
        self.tile_group = 0 # I think this should be tile_type
        self.tile_variant = 0
        self.grid_on = True

    def run(self):
        '''The main game loop.'''
        while True:
            self.display.fill((0, 0, 0, 0))
            
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 3
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 3
            
            self.rounded_scroll = pg.Vector2((floor(self.scroll[0]), floor(self.scroll[1])))
            
            self.tilemap.render(self.display, offset=self.rounded_scroll)
            
            current_tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
           # current_tile_image.set_alpha(150)
            
            mouse_pos = pg.Vector2(pg.mouse.get_pos()) / RENDER_SCALE
            #tile_pos should be mouse_coord
            tile_pos = (mouse_pos + self.rounded_scroll) / self.tilemap.tile_size
            tile_pos_rounded = (floor(tile_pos[0]), floor(tile_pos[1]))
            if self.grid_on:
                self.display.blit(current_tile_image, (tile_pos_rounded[0] * self.tilemap.tile_size - self.rounded_scroll[0], tile_pos_rounded[1] * self.tilemap.tile_size - self.rounded_scroll[1]))
            else:
                self.display.blit(current_tile_image, (mouse_pos))
                

            # this should probably go after the event queue
            if self.clicking and self.grid_on:
                tile_clicked = str(tile_pos_rounded[0]) + ';' + str(tile_pos_rounded[1])
                self.tilemap.tilemap[tile_clicked] = {
                    'type': self.tile_list[self.tile_group],
                    'variant': self.tile_variant,
                    'pos': tile_pos_rounded,
                    }
            if self.right_clicking:
                tile_hovered = str(tile_pos_rounded[0]) + ';' + str(tile_pos_rounded[1])
                if tile_hovered in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_hovered]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_image = self.assets[tile['type']][tile['variant']]
                    tile_rect = pg.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_image.get_width(), tile_image.get_height())
                    if tile_rect.collidepoint(mouse_pos):
                        self.tilemap.offgrid_tiles.remove(tile)


            #current selected in top left
            self.display.blit(current_tile_image, (0, 0))

            
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.grid_on:
                            # maybe should round the mouse pos for this
                            self.tilemap.offgrid_tiles.append({
                                'type': self.tile_list[self.tile_group],
                                'variant': self.tile_variant,
                                'pos': (mouse_pos[0] + self.scroll[0], mouse_pos[1] + self.scroll[1]),
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


            self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (0,0))
            
            pg.display.update()
            self.clock.tick(60)


Editor().run()