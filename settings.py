"""Module containing all game settings for Alien Invasion."""


class Settings:
    """A class to store all settings for Alien Invasion.
    
    Attributes:
        screen_width: The width of the game window in pixels.
        screen_height: The height of the game window in pixels.
        bg_color: RGB tuple for the background color.
        ship_speed: The normal speed of the ship in pixels per frame.
        ship_turbo_speed: The turbo speed of the ship in pixels per frame.
        bullet_speed: The speed of bullets moving right in pixels per frame.
        bullet_width: The width of bullets in pixels.
        bullet_height: The height of bullets in pixels.
        bullet_color: RGB tuple for the bullet color.
        bullets_allowed: Maximum number of bullets on screen at once.
        alien_speed: The speed of aliens moving left in pixels per frame.
        alien_spawn_rate: The number of aliens to create per row.
    """

    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_speed = 1.5
        self.ship_turbo_speed = 6.0
        self.ship_limit = 3

        # Bullet settings
        self.bullet_speed = 2.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3

        # Alien settings
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1