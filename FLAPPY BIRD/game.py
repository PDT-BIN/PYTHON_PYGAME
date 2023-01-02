import sys
from random import choice

import pygame

from Bird import Bird
from Display import Display
from Floor import Floor
from Pipe import Pipe
from Scoreboard import Scoreboard
from Setting import Setting


class FlappyBird:
    """A class to mange game assets and behaviors."""

    def __init__(self):
        # Initialize necessary model.
        pygame.mixer.pre_init(frequency=44100, size=-
                              16, channels=2, buffer=512)
        pygame.init()
        # Set up for setting.
        self.setting = Setting()
        # Set up for screen.
        self.screen = pygame.display.set_mode(
            (self.setting.screen_width, self.setting.screen_height))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        # Set up for display.
        self.display = Display(self)
        # Set up for game objects.
        self.floor = Floor(self)
        self.pipes = pygame.sprite.Group()
        self.bird = Bird(self)
        # Set up for score.
        self.scoreboard = Scoreboard(self)
        # Set up for custom events.
        # Create pipes on screen.
        self.spawnpipe = pygame.USEREVENT
        pygame.time.set_timer(self.spawnpipe, 1200)
        # Create bird flap effect.
        self.birdflap = pygame.USEREVENT + 1
        pygame.time.set_timer(self.birdflap, 200)
        # Create getting point effect.
        self.getpoint = pygame.USEREVENT + 2
        pygame.time.set_timer(self.getpoint, 1000)

    def run_game(self):
        """Start the main loop for game."""
        while True:
            self._check_event()
            self._update_screen()
            self.clock.tick(120)

    def _check_event(self):
        """Catch the event from user."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            # Check custom events.
            if self.display.game_active:
                if event.type == self.spawnpipe:
                    self._spawn_pipe()
                if event.type == self.getpoint:
                    self._get_point()
                if event.type == self.birdflap:
                    self.bird.flap_animation()
            # Check user events.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.display.game_active:
                        self._start_game()
                    else:
                        self.display.flap_sound.play()
                        self.bird.fly_up()

    def _update_screen(self):
        """Update movement & Draw object."""
        # Always draw.
        self.display.draw_BACKGROUND()
        self.scoreboard.draw(self.display.game_active)
        # Draw according to the display.
        if self.display.game_active:
            self._update_bird()
            self._update_pipe()
            self.bird.draw(self.bird.rotate())
            self.pipes.draw(self.screen)
        else:
            self.display.draw_USERGUIDE()
            if self.display.game_over:
                self.display.draw_GAMEOVER()
        # Draw in front of the pipes.
        self.floor.update()
        self.floor.draw()
        pygame.display.update()

    # ------------------------------------------------------ START & QUIT ------------------------------------------------------
    def _start_game(self):
        """Start the (new) game."""
        # Reset screen.
        self.bird.reset()
        self.pipes.empty()
        # Reset dynamic attributes.
        self.scoreboard.reset_score()
        # Prepare initial images.
        self.scoreboard.prep_image()
        # Set up control flags.
        self.display.game_active = True
        self.display.game_over = False

    def _quit_game(self):
        """Quit game."""
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------ CUSTOM EVENT ------------------------------------------------------
    def _get_point(self):
        """Add point to the score of player each 1 second."""
        self.display.point_sound.play()
        self.scoreboard.score += 1
        self.scoreboard.prep_score()

    def _spawn_pipe(self):
        """Create new pipes and add it to its list."""
        bottom_pipe, top_pipe = Pipe(self), Pipe(self)
        rand_pipe_height_pos = choice(self.setting.pipe_height_list)
        # Set up for bottom pipe.
        bottom_pipe.rect.midtop = (500, rand_pipe_height_pos)
        # Set up for top pipe.
        top_pipe.image = pygame.transform.flip(top_pipe.image, False, True)
        top_pipe.rect.midtop = (500, rand_pipe_height_pos - 700)
        # Add them to their list.
        self.pipes.add(top_pipe)
        self.pipes.add(bottom_pipe)

    # ----------------------------------------------------- UPDATE MOVEMENT -----------------------------------------------------
    def _update_bird(self):
        """Update bird movement & Check collision."""
        self.bird.update()
        self._check_collision()

    def _update_pipe(self):
        """Update pipes movement & Remove pipes that were out of screen."""
        self.pipes.update()
        for pipe in self.pipes.copy():
            if pipe.rect.right <= 0:
                self.pipes.remove(pipe)

    def _check_collision(self):
        """Check the collision of bird with other objects."""
        if pygame.sprite.spritecollideany(self.bird, self.pipes) or (self.bird.rect.top <= 0 or self.bird.rect.bottom >= 650):
            self.display.hit_sound.play()
            self.scoreboard.update_score()
            self.display.game_active = False
            self.display.game_over = True


if __name__ == '__main__':
    FB = FlappyBird()
    FB.run_game()
