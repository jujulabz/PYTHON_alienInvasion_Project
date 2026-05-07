

"""Milestone 3 aliens shooting back """

import pygame 
from pygame.sprite import Sprite


class AlienBullet(Sprite):
    """Class to manage alien bullets"""
    
    def __init__(self, ai_game, alien):
        """Creating alien bullet at the aliens current position"""
        
        super().__init__()
        
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = (255, 0 ,0)
        
        self.rect = pygame.Rect(0, 0, 4, 15)
        self.rect.midtop = alien.rect.midbottom
        
        self.y = float(self.rect.y)
        
    def update(self):
        """Move the alien bullet down the screen"""
        
        self.y += self.settings.alien_bullet_speed
        self.rect.y = self.y
        
        
    def draw_bullet(self):
        """Draws the alien bullet"""
        pygame.draw.rect(self.screen, self.color, self.rect)
        
        