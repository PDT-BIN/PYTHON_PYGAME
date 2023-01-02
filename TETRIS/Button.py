from pygame.transform import scale
from pygame.image import load
from pygame.mouse import get_pos


class Button:
    """A class to manage interactive button."""
    # BUTTON IMAGE.
    BUTTONS = [load(f'image/BUTTON/BTN_{i}.png') for i in range(3)]

    def __init__(self, TG, text: str, text_color: tuple, kind: int, size: tuple, position: tuple):
        self.screen = TG.screen
        self.setting = TG.setting
        self.text_color = text_color
        # BUTTON IMAGE.
        self.image = scale(Button.BUTTONS[kind], size)
        self.rect = self.image.get_rect(x=position[0], y=position[1])
        # TEXT IMAGE.
        self.text_image = self.setting.FONT.render(text, True, self.text_color)
        self.text_rect = self.text_image.get_rect(center=self.rect.center)

    def is_clicked(self) -> bool:
        """Check if button is clicked."""
        return self.rect.collidepoint(get_pos())

    def draw(self):
        """Draw button."""
        self.screen.blit(self.image, self.rect)
        self.screen.blit(self.text_image, self.text_rect)
