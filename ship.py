"""Module for managing the player's ship in the Alien Invasion game."""

import pygame


class Ship:
    """A class to manage the player's ship.
    
    The ship can move in all four directions (up, down, left, right) and
    can fire bullets. It includes a turbo mode for increased speed.
    
    Attributes:
        screen: The pygame display surface.
        settings: The game settings object.
        screen_rect: The rect of the game screen.
        image: The pygame image for the ship.
        rect: The rect object for the ship's image.
        x: The ship's x-coordinate as a float.
        y: The ship's y-coordinate as a float.
        moving_right: Flag indicating if the ship should move right.
        moving_left: Flag indicating if the ship should move left.
        moving_up: Flag indicating if the ship should move up.
        moving_down: Flag indicating if the ship should move down.
        moving_turbo: Flag indicating if turbo speed is active.
    """

    def __init__(self, ai_game):
        """Initialize the ship and set its starting position.
        
        Args:
            ai_game: The AlienInvasion game instance containing screen
                    and settings.
        """
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # Start the ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

        # Store ship's position as float for smooth movement.
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Movement flags.
        self.moving_right = False
        self.moving_left = False
        self.moving_turbo = False
        self.moving_up = False
        self.moving_down = False

    def update(self):
        """Update the ship's position based on movement flags.
        
        The ship moves with normal speed or turbo speed (if activated).
        Boundaries prevent the ship from moving off the edges of the screen.
        """
        # Determine speed based on turbo flag.
        speed = self.settings.ship_turbo_speed if self.moving_turbo else self.settings.ship_speed

        # Update horizontal position.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += speed
        if self.moving_left and self.rect.left > 0:
            self.x -= speed

        # Update vertical position.
        if self.moving_up and self.rect.top > 0:
            self.y -= speed
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += speed

        # Update rect position from float coordinates.
        self.rect.x = self.x
        self.rect.y = self.y

    def blitme(self):
        """Draw the ship at its current location on the screen."""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """Center the ship on the screen.
        
        Resets the ship's position to the center bottom of the screen.
        Used when the ship is hit or the game restarts.
        """
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)