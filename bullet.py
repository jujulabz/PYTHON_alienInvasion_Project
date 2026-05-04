"""Module for managing bullets fired by the player's ship."""

import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """A class to manage bullets fired from the ship.
    
    Bullets spawn at the top of the ship and move vertically upward.
    They are removed from the game when they move off-screen.
    
    Attributes:
        screen: The pygame display surface.
        settings: The game settings object.
        color: RGB tuple for the bullet color.
        rect: The rect object for the bullet.
        y: The bullet's y-coordinate as a float.
    """

    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position.
        
        Args:
            ai_game: The AlienInvasion game instance containing screen,
                    settings, and ship information.
        """
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
            self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # Store the bullet's position as a float.
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet vertically upward across the screen.
        
        Updates the bullet's position based on the configured bullet speed.
        """
        # Update the exact position of the bullet.
        self.y -= self.settings.bullet_speed
        # Update the rect position.
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet as a rectangle on the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)