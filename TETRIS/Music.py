from pygame.transform import scale
from pygame.image import load
from pygame.mixer import music, Sound


class Music:
    """A class to manage music."""

    def __init__(self, TG):
        self.screen = TG.screen
        self.setting = TG.setting
        # SPEAKER IMAGE.
        self.SPEAKERS = [
            scale(load(f'image/SPEAKER/SP_{i}.png'), (50, 50)) for i in range(2)]
        self.SPEAKERS_RECT = (0, 0)
        # MUSICS & SOUNDS.
        music.load('sound/GAME_MUSIC.wav')
        self.SOUNDS = [Sound(f'sound/SOUND_{i}.wav') for i in range(2)]
        # CONTROL FLAG.
        self.control_flag = True
        music.play(-1)

    def play_music(self):
        """Play background music."""
        self.control_flag = not self.control_flag
        music.unpause() if self.control_flag else music.pause()

    def play_sound(self, kind: int):
        """Play sounds."""
        if self.control_flag:
            self.SOUNDS[kind].play()

    def draw_speaker(self):
        """Draw speaker image."""
        self.screen.blit(
            self.SPEAKERS[0] if self.control_flag else self.SPEAKERS[1], self.SPEAKERS_RECT)
