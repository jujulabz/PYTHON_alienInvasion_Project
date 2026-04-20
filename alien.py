"""Module for managing alien enemies in the Alien Invasion game."""

import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """A class to manage individual aliens in the game.
    
    Aliens spawn on the right side of the screen and move horizontally
    toward the left. They are destroyed when hit by bullets.
    """

    def __init__(self, ai_game):
        """Initialize an alien and set its starting position.
        
        Args:
            ai_game: The AlienInvasion game instance containing screen,
                    settings, and other game resources.
        """
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and get its rect.
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien near the top right of the screen.
        self.rect.x = self.screen.get_rect().right
        self.rect.y = self.rect.height

        # Store the alien's exact x position.
        self.x = float(self.rect.x)

    def update(self):
        """Move the alien right or left based on fleet direction.
        
        The alien's movement direction is controlled by the fleet_direction
        setting, which changes when the fleet reaches a screen edge.
        """
        # Update the exact position of the alien based on fleet direction.
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        # Update the rect position.
        self.rect.x = self.x

    def check_edges(self):
        """Return True if alien is at an edge of the screen.
        
        Checks both the right and left edges of the screen to determine
        when the fleet should bounce and change direction.
        
        Returns:
            True if the alien is at the right or left edge of the screen,
            False otherwise.
        """
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)
