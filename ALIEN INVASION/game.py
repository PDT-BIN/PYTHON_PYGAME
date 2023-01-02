import sys
from time import sleep

import pygame

from Alien import Alien
from Bullet import Bullet
from Button import Button
from Display import Display
from Game_Statistic import GameStats
from Scoreboard import Scoreboard
from Setting import Setting
from Ship import Ship


class AlienInvasion:
    """Overall class to manage game assets and behaviors."""

    def __init__(self):
        # Active all modules of pygame.
        pygame.init()
        # Use the default resource from setting.py.
        self.setting = Setting()
        # Set up for screen.
        self.screen = pygame.display.set_mode(
            (self.setting.screen_width, self.setting.screen_height))
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption("Alien Invasion")
        # Set up for game statistic.
        self.stats = GameStats(self)
        # Set up for scoreboard.
        self.scoreboard = Scoreboard(self)
        # Set up for ship.
        self.ship = Ship(self)
        # Set up for bullet.
        self.bullets = pygame.sprite.Group()
        # Set up for alien.
        self.aliens = pygame.sprite.Group()
        # Set up for button.
        self.play_button = Button(
            self, 'PLAY', (self.screen_rect.centerx, self.screen_rect.centery + 50))
        self.about_button = Button(
            self, 'ABOUT', (self.screen_rect.centerx, self.screen_rect.centery + 150))
        self.quit_button = Button(
            self, 'QUIT', (self.screen_rect.centerx, self.screen_rect.centery + 250))
        # Challenges.
        self.challenge = False
        self.easy_button = Button(
            self, 'EASY', (self.screen_rect.centerx, self.screen_rect.centery + 50))
        self.normal_button = Button(
            self, 'NORMAL', (self.screen_rect.centerx, self.screen_rect.centery + 150))
        self.hard_button = Button(
            self, 'HARD', (self.screen_rect.centerx, self.screen_rect.centery + 250))
        # Set up for display.
        self.display = Display(self)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self.display.play_music()
            self.display.stop_music()
            self._check_events()
            self._update_screen()

# -------------------------------------------------------- START & QUIT --------------------------------------------------------
    def _start_game(self):
        """Start game."""
        # Active the game.
        self.stats.game_active = True
        # Start the dynamic game statistics and settings.
        self.setting.initialize_dynamic_settings()
        self.stats.reset_statistic()
        self.scoreboard.prep_images()
        # Set up the screen.
        self._set_screen()
        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)

    def _start_new_level(self):
        """Start a new game with higher level."""
        # Set up the screen.
        self._set_screen()
        # Speed up game.
        self.setting.increase_speed()
        # Increase level of game.
        self.stats.level += 1
        self.scoreboard.prep_level()

    def _quit_game(self):
        """Quit game."""
        self.scoreboard.save_score()
        pygame.quit()
        sys.exit()

# -------------------------------------------------------- CHECK EVENT --------------------------------------------------------
    def _check_events(self):
        """Catch keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self._quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._check_mousebuttondown_event()
            else:
                if self.stats.game_active:
                    if event.type == pygame.KEYDOWN:
                        self._check_keydown_events(event)
                    elif event.type == pygame.KEYUP:
                        self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Catch keydown from keyboard."""
        if event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_RIGHT:
            self.ship.moving_right = True

    def _check_keyup_events(self, event):
        """Catch keyup from keyboard."""
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_RIGHT:
            self.ship.moving_right = False

    def _check_mousebuttondown_event(self):
        """Catch the mouse event."""
        # Check click button to turn its display on.
        if not self.stats.game_active and not self.display.user_guide and not self.display.game_over and not self.challenge:
            self._check_MENU_buttons()
        else:
            # Check click challenge buttons.
            if self.challenge:
                self._check_CHALLENGE_buttons()
            # Check click screen.
            if self._check_click_screen():
                self._turn_off_flag()

    def _check_click_button(self, button):
        """Check if player clicks the button."""
        mouse_pos = pygame.mouse.get_pos()
        return button.rect.collidepoint(mouse_pos)

    def _check_click_screen(self):
        """Check if player clicks on the screen."""
        mouse_pos = pygame.mouse.get_pos()
        return self.screen_rect.collidepoint(mouse_pos)

    def _check_MENU_buttons(self):
        """Check click menu buttons."""
        # Click 'PLAY'.
        if self._check_click_button(self.play_button):
            self.challenge = True
        # Click 'ABOUT'.
        elif self._check_click_button(self.about_button):
            self.display.user_guide = True
        # Click 'QUIT'.
        elif self._check_click_button(self.quit_button):
            self._quit_game()

    def _check_CHALLENGE_buttons(self):
        """Check click challenge buttons."""
        # Click 'EASY'
        if self._check_click_button(self.easy_button):
            self._challenge_choice()
        # Click 'NORMAL'
        elif self._check_click_button(self.normal_button):
            self._challenge_choice(2, 2, 2.25)
         # Click 'HARD'
        elif self._check_click_button(self.hard_button):
            self._challenge_choice(1, 1, 2.5)

    def _challenge_choice(self, life_limit=3, bullet_allowed=3, alien_speed=1.5):
        """Set up the settings for challenge."""
        self.setting.life_limit = life_limit
        self.setting.bullet_allowed = bullet_allowed
        self.setting.alien_speed = alien_speed
        self.challenge = False
        self._start_game()

    def _turn_off_flag(self):
        """Check display flag to turn it off."""
        # Turn off 'GAME OVER'.
        if self.display.game_over:
            self.display.game_over = False
        # Turn off 'USER GUIDE'.
        elif self.display.user_guide:
            self.display.user_guide = False
        # Turn off 'CHALLENGE'.
        elif self.challenge:
            self.challenge = False

# -------------------------------------------------------- BULLET OBJECT --------------------------------------------------------
    def _fire_bullet(self):
        """Add a new bullet to the bullet list when player click 'SPACE'."""
        if len(self.bullets) < self.setting.bullet_allowed:
            self.display.play_sound(self.display.bullet_sound)
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update movement of bullets."""
        self.bullets.update()
        # Check if any bullets have been out of screen, remove them.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # Check if any bullets have collided with aliens.
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Remove bullet and alien that collided from their list."""
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        # Scoring all the aliens that were defeated by player.
        if collisions:
            for aliens in collisions.values():
                self.stats.score += (self.setting.alien_point * len(aliens))
                self.scoreboard.prep_score()
                self.scoreboard.check_highest_score()
        # Check if all aliens have been defeated, start new level.
        if not self.aliens:
            self._start_new_level()

# -------------------------------------------------------- ALIEN OBJECT --------------------------------------------------------
    def _create_fleet(self):
        """Create a alien fleet."""
        # Get necessary image information.
        alien_tmp = Alien(self)
        alien_width, alien_height = alien_tmp.rect.size
        ship_height = self.ship.rect.height
        scoreboard_height = self.scoreboard.score_bar_image_rect.height
        # Determine the number of aliens on a row.
        available_space_x = self.setting.screen_width - (2 * alien_width)
        alien_quantity = available_space_x // (2 * alien_width)
        # Determine the number of rows on the screen.
        available_space_y = self.setting.screen_height - \
            (2 * alien_height) - (ship_height + scoreboard_height)
        row_quantity = available_space_y // (2 * alien_height)
        # Create alien fleet.
        for row_number in range(row_quantity):
            for alien_number in range(alien_quantity):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien."""
        # Get necessary image information.
        new_alien = Alien(self)
        alien_width, alien_height = new_alien.rect.size
        scoreboard_height = self.scoreboard.score_bar_image_rect.height
        # Put the alien on its correct position on its row.
        new_alien.x = alien_width + (2 * alien_width * alien_number)
        new_alien.rect.x = new_alien.x
        new_alien.rect.y = scoreboard_height + (2 * alien_height * row_number)
        # Add an alien element to the alien list.
        self.aliens.add(new_alien)

    def _check_fleet_edge(self):
        """Check if any alien of fleet reached the edge of the screen."""
        for alien in self.aliens.sprites():
            # Check one by one alien.
            if alien.check_edge():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the fleet and change its direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.setting.fleet_drop_speed
        self.setting.fleet_direction *= -1

    def _update_aliens(self):
        """Update movement of aliens."""
        self._check_fleet_edge()
        self.aliens.update()
        # Check if any aliens have collided with the ship.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Check if any aliens have reached the bottom of the screen.
        self._check_alien_bottom_collisions()

    def _ship_hit(self):
        """The player has been defeated by alien."""
        if self.stats.life_points > 0:
            # Decrease the ship lifes.
            self.stats.life_points -= 1
            # Reset the screen.
            self._set_screen()
            # Pause.
            sleep(1.0)
        else:
            self.stats.game_active = False
            self.display.game_over = True
            pygame.mouse.set_visible(True)

    def _check_alien_bottom_collisions(self):
        """Reset the screen when any aliens hit the bottom of screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.screen_rect.bottom:
                self._ship_hit()
                break

# -------------------------------------------------------- DRAW SCREEN --------------------------------------------------------
    def _draw_MENU(self):
        """Draw the menu of game when player is in 'MENU' display."""
        self.display.draw_BACKGROUND()
        self.play_button.draw_button()
        self.about_button.draw_button()
        self.quit_button.draw_button()

    def _draw_CHALLENGE(self):
        """Draw the challenges table for player to choose."""
        self.easy_button.draw_button()
        self.normal_button.draw_button()
        self.hard_button.draw_button()

    def _draw_screen(self):
        """Draw what is happenning on the screen currently."""
        self.ship.draw_ship()
        self.bullets.draw(self.screen)
        self.aliens.draw(self.screen)
        self.scoreboard.draw_scoreboard()

    def _set_screen(self):
        """Clear anythings remainning on screen and set up a new game."""
        self.bullets.empty()
        self.aliens.empty()
        self._create_fleet()
        self.ship.center_ship()

    def _update_screen(self):
        """Draw the game display if game is active else draw the appointed display."""
        if self.stats.game_active:
            # Update the movement of all objects and draw them onto the screen.
            self.ship.update()
            self._update_bullets()
            self._update_aliens()
            self.screen.fill(self.setting.bg_color)
            self._draw_screen()
        else:
            if self.challenge:
                self._draw_CHALLENGE()
            elif self.display.user_guide:
                self.display.draw_USER_GUIDE()
            elif self.display.game_over:
                self.display.draw_GAME_OVER()
            else:
                self._draw_MENU()
        pygame.display.flip()


if __name__ == '__main__':
    AI = AlienInvasion()
    AI.run_game()
