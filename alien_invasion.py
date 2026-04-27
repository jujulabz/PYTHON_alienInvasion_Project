"""Main module for the Alien Invasion game.

This module manages the overall game state, including the main game loop,
event handling, and coordination between game objects (ship, bullets, aliens).
"""

import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
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
        ships_left: Number of ships remaining for the player.
    """

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        self.stats = GameStats(self)
        self.game_active = True

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
    
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height
    
    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._check_bullet_alien_collisions()

            self._update_screen()
            self.clock.tick(60)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions.
        
        Calls _check_fleet_edges() to handle bouncing behavior, then
        updates all alien positions.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            print("Ship hit!!!")
            
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

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
        self.ship.blitme()
        # Draw all active aliens.
        self.aliens.draw(self.screen)

        # Draw game over message if game is not active.
        if not self.game_active:
            self._draw_game_over()

        pygame.display.flip()

    # Milestone 2: Add game over message and restart functionality
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

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                 self.bullets.remove(bullet)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge.
        
        Checks all aliens to see if any have reached the right or left edge
        of the screen. If so, changes the fleet direction and drops the fleet.
        """
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left.
            self.stats.ships_left -= 1

        # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.game_active = False

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break
#Milestone 2
    def _check_bullet_alien_collisions(self):
        """Check for collisions between bullets and aliens.
        
        Remove any bullets and aliens that have collided.
        """
        # Check for any bullets that have hit aliens.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            print(f"Aliens destroyed: {len(collisions)}")
#Milestone 2
    def _restart_game(self):
        """Restart the game after game over."""
        # Reset game stats.
        self.stats.reset_stats()
        self.game_active = True

        # Clear bullets and aliens.
        self.bullets.empty()
        self.aliens.empty()

        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()