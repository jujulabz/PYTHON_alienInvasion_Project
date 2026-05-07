"""Main module for the Alien Invasion game.

This module manages the overall game state, including the main game loop,
event handling, and coordination between game objects (ship, bullets, aliens).
"""

import sys
from random import choice, random
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
# Milestone 3: Import alien bullets so aliens can shoot back.
from alien_bullets import AlienBullet


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
        self.game_active = False
        self.game_over = False
        self.restart_grace_frames = 0

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        self.clock = pygame.time.Clock()
        self.screen_rect = self.screen.get_rect()

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        # Milestone 3: Group for bullets fired by aliens.
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        # Milestone 2: Create the Play, Play Again, and Quit buttons.
        self._create_buttons()

        self.bg_color = self.settings.bg_color

    def _create_buttons(self):
        """Create the play, play again, and quit buttons."""
        # Milestone 2: Set up the start and game-over buttons.
        self.button_font = pygame.font.SysFont(None, 48)
        self.title_font = pygame.font.SysFont(None, 84)
        self.play_button = self._make_button("Play", self.screen_rect.center)
        self.play_again_button = self._make_button(
            "Play Again", (self.screen_rect.centerx, self.screen_rect.centery + 45))
        self.quit_button = self._make_button(
            "Quit", (self.screen_rect.centerx, self.screen_rect.centery + 125))

    def _make_button(self, message, center):
        """Return a simple button with its rendered label."""
        button_color = (40, 120, 90)
        text_color = (255, 255, 255)
        rect = pygame.Rect(0, 0, 260, 64)
        rect.center = center
        image = self.button_font.render(message, True, text_color, button_color)
        image_rect = image.get_rect()
        image_rect.center = rect.center
        return {
            "rect": rect,
            "image": image,
            "image_rect": image_rect,
            "color": button_color,
        }
    
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
                self._update_alien_bullets()
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Milestone 2: Let players click Play, Play Again, or Quit.
                self._check_mouse_events(event.pos)

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

    def _check_mouse_events(self, mouse_pos):
        """Respond to mouse clicks on menu and game-over buttons."""
        # Milestone 2: Handle Play, Play Again, and Quit button clicks.
        if self.game_active:
            return

        if self.game_over:
            if self.play_again_button["rect"].collidepoint(mouse_pos):
                self._restart_game()
            elif self.quit_button["rect"].collidepoint(mouse_pos):
                sys.exit()
        elif self.play_button["rect"].collidepoint(mouse_pos):
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

    def _fire_alien_bullet(self):
        """Randomly fire one alien bullet from a living alien."""
        # Milestone 3: Randomly let aliens shoot back at the player.
        if not self.aliens:
            return

        if self.restart_grace_frames > 0:
            self.restart_grace_frames -= 1
            return

        if len(self.alien_bullets) >= self.settings.alien_bullets_allowed:
            return

        if random() < self.settings.alien_fire_chance:
            alien = choice(self.aliens.sprites())
            self.alien_bullets.add(AlienBullet(self, alien))

    def _update_screen(self):
        """Update images on the screen and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)

        if self.game_active:
            # Draw all active bullets.
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            # Milestone 3: Draw alien bullets.
            for bullet in self.alien_bullets.sprites():
                bullet.draw_bullet()
            self.ship.blitme()
            # Draw all active aliens.
            self.aliens.draw(self.screen)

        if not self.game_active and self.game_over:
            self._draw_game_over()
        elif not self.game_active:
            self._draw_start_screen()

        pygame.display.flip()

    def _draw_button(self, button):
        """Draw one button on the screen."""
        pygame.draw.rect(self.screen, button["color"], button["rect"])
        self.screen.blit(button["image"], button["image_rect"])

    def _draw_start_screen(self):
        """Draw the opening play screen."""
        # Milestone 2: Draw the opening Play button screen.
        title_image = self.title_font.render("Alien Invasion", True, (30, 30, 30))
        title_rect = title_image.get_rect()
        title_rect.center = (self.screen_rect.centerx, self.screen_rect.centery - 90)
        self.screen.blit(title_image, title_rect)
        self._draw_button(self.play_button)

    # Milestone 2: Add game over message and Play Again/Quit buttons.
    def _draw_game_over(self):
        """Draw the game over message on the screen."""
        game_over_text = self.title_font.render("Game Over", True, (180, 0, 0))
        text_rect = game_over_text.get_rect()
        text_rect.center = (self.screen_rect.centerx, self.screen_rect.centery - 80)
        self.screen.blit(game_over_text, text_rect)
        self._draw_button(self.play_again_button)
        self._draw_button(self.quit_button)

    def _update_bullets(self):
        """Update position of bullets and remove off-screen bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                 self.bullets.remove(bullet)

    def _update_alien_bullets(self):
        """Update alien bullets and check whether they hit the ship."""
        # Milestone 3: Move alien bullets and check if they hit the ship.
        self._fire_alien_bullet()
        self.alien_bullets.update()

        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)

        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()

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
        if self.stats.ships_left > 1:
            self.stats.ships_left -= 1

            # Create a new fleet and center the ship.
            self.bullets.empty()
            self.alien_bullets.empty()
            self.aliens.empty()
            self.settings.fleet_direction = 1
            self.restart_grace_frames = 90
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.stats.ships_left = 0
            self.game_active = False
            self.game_over = True
            self.bullets.empty()
            self.alien_bullets.empty()
            self.aliens.empty()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break
# Milestone 2
    def _check_bullet_alien_collisions(self):
        """Check for collisions between bullets and aliens.
        
        Remove any bullets and aliens that have collided.
        """
        # Check for any bullets that have hit aliens.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            print(f"Aliens destroyed: {len(collisions)}")
# Milestone 2: Restart the game after pressing P or Play Again.
    def _restart_game(self):
        """Restart the game after game over."""
        # Reset game stats.
        self.stats.reset_stats()
        self.game_active = True

        # Clear bullets and aliens.
        self.bullets.empty()
        self.alien_bullets.empty()
        self.aliens.empty()
        self.settings.fleet_direction = 1
        self.game_over = False
        self.restart_grace_frames = 90

        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
