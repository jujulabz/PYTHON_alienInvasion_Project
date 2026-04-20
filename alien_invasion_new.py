"""Main module for the Alien Invasion game.

This module manages the overall game state, including the main game loop,
event handling, and coordination between game objects (ship, bullets, aliens).
"""

import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    """Overall class to manage game assets and behavior.
    
    Attributes:
        settings: The game settings object.
        screen: The pygame display surface.
        clock: Pygame clock for controlling frame rate.
        ship: The player's ship object.
        bullets: Pygame sprite group containing active bullets.
        aliens: Pygame sprite group containing active aliens.
        game_active: Boolean indicating if the game is currently running.
        bg_color: RGB tuple for the background color.
    """

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        self.clock = pygame.time.Clock()

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        self.bg_color = self.settings.bg_color
        self.game_active = True

    def _create_fleet(self):
        """Create the fleet of aliens.
        
        Aliens are spawned in a grid pattern on the right side of the screen,
        moving horizontally to the left toward the player.
        """
        # Create aliens and add them to the group.
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height

        # Calculate how many aliens fit on screen.
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        available_space_y = self.settings.screen_height - (3 * alien_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the fleet.
        
        Args:
            alien_number: The horizontal position index of the alien.
            row_number: The vertical position (row) index of the alien.
        """
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height

        alien.x = self.settings.screen_width - (alien_width + 2 * alien_width * alien_number)
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number

        self.aliens.add(alien)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._check_collisions()
                self._check_loss_conditions()

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Respond to keypresses.
        
        Args:
            event: The pygame key event.
        """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_LSHIFT:
            self.ship.moving_turbo = True
        elif event.key == pygame.K_p:
            if not self.game_active:
                self._restart_game()

    def _check_keyup_events(self, event):
        """Respond to key releases.
        
        Args:
            event: The pygame key event.
        """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False
        elif event.key == pygame.K_LSHIFT:
            self.ship.moving_turbo = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group.
        
        Respects the maximum bullet limit set in settings.
        """
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_screen(self):
        """Update images on the screen and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)

        # Draw all active bullets.
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # Draw all active aliens.
        self.aliens.draw(self.screen)

        # Draw the ship.
        self.ship.blitme()

        # Draw game over text if needed.
        if not self.game_active:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_game_over(self):
        """Draw the game over message on the screen."""
        font = pygame.font.SysFont(None, 80)
        game_over_text = font.render("Game Over! Press P to Play Again", True, (255, 0, 0))
        text_rect = game_over_text.get_rect()
        text_rect.center = self.screen.get_rect().center
        self.screen.blit(game_over_text, text_rect)

    def _update_bullets(self):
        """Update position of bullets and remove off-screen bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Remove bullets that have moved off screen to the right.
        for bullet in self.bullets.copy():
            if bullet.rect.left >= self.settings.screen_width:
                self.bullets.remove(bullet)

    def _update_aliens(self):
        """Update the position of all aliens."""
        self.aliens.update()

    def _check_collisions(self):
        """Check for collisions between bullets and aliens.
        
        When a bullet hits an alien, both are removed from the game.
        When all aliens are destroyed, a new fleet is created.
        """
        # Check for bullet-alien collisions.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        # If all aliens are destroyed, create a new fleet.
        if len(self.aliens) == 0:
            self.bullets.empty()
            self._create_fleet()

    def _check_loss_conditions(self):
        """Check loss conditions for the game.
        
        The game ends if:
        1. An alien collides with (reaches) the ship.
        2. An alien reaches the left edge of the screen (behind the ship).
        """
        # Check if any alien has collided with the ship.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._game_over()

        # Check if any alien has passed the left edge of the screen.
        for alien in self.aliens:
            if alien.rect.left <= 0:
                self._game_over()

    def _game_over(self):
        """End the game and display game over state."""
        self.game_active = False

    def _restart_game(self):
        """Restart the game by resetting all game objects."""
        self.bullets.empty()
        self.aliens.empty()
        self._create_fleet()
        self.ship.rect.midbottom = self.screen.get_rect().midbottom
        self.ship.x = float(self.ship.rect.x)
        self.ship.y = float(self.ship.rect.y)
        self.game_active = True


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
