import pygame as pg

class Button:
    def __init__(self, rect, command):
        self.color = (50,150,75)
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size)
        self.image.fill(self.color)
        self.command = command
    def render(self, screen):
        screen.blit(self.image, self.rect)
    def get_event(self, event, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.command()