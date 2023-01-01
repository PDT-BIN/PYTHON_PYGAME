from pygame import Rect, Surface
from pygame.image import load
from pygame.math import Vector2


class Snake:
    '''A class to manage snake object.'''

    def __init__(self, screen: Surface) -> None:
        '''Initialize core attributes.'''
        self.__screen, self.__dim = screen, Vector2(screen.get_size())
        self.__size = 20
        # IMAGE STORAGE.
        self.__images = tuple(tuple(load(f'image/SNAKE/{P}_{i}.png').convert_alpha() for i in range(N))
                              for P, N in (('HEAD', 4), ('BODY', 6), ('TAIL', 4)))
        # CREATE AT FIRST.
        self.refresh()

    @property
    def speed(self) -> int:
        return self.__speed

    @speed.setter
    def speed(self, value: int) -> None:
        self.__speed = value if 20 <= value <= 130 else 20 if self.__speed < 20 else 130

    @property
    def shifter(self) -> str:
        return self.__shifter

    @shifter.setter
    def shifter(self, value: str) -> None:
        self.__shifter = value

    def refresh(self) -> None:
        '''Refresh appearance position, length, speed & direction of snake.'''
        self.__lead = Vector2(self.__dim.x / 2, self.__dim.y / 2)
        self.__rect = Rect(self.__lead, (self.__size, self.__size))
        self.__body = [self.__lead - (i * self.__size, 0) for i in range(4)]
        self.__shifter = self.__direction = 'R'
        self.__speed = 0

# MOVEMENT.
    def update(self) -> None:
        '''Update movement.'''
        self.__shift()
        match self.__direction:
            case 'L':
                self.__lead.x -= self.__size
            case 'R':
                self.__lead.x += self.__size
            case 'U':
                self.__lead.y -= self.__size
            case 'D':
                self.__lead.y += self.__size

    def __shift(self) -> None:
        '''Change direction.'''
        match self.__shifter:
            case 'L' if not self.__direction == 'R':
                self.__direction = self.__shifter
            case 'R' if not self.__direction == 'L':
                self.__direction = self.__shifter
            case 'U' if not self.__direction == 'D':
                self.__direction = self.__shifter
            case 'D' if not self.__direction == 'U':
                self.__direction = self.__shifter

# COLLISION.
    def is_ate(self, fruit_rect: Rect) -> bool:
        '''Check if snake ate fruit.'''
        self.__body.insert(0, self.__lead.copy())
        self.__rect.topleft = self.__lead
        return self.__rect.colliderect(fruit_rect) or self.__body.pop() and False

    def is_drank(self, drink_rect: Rect) -> bool:
        '''Check if snake drank drink.'''
        return self.__rect.colliderect(drink_rect)

    def is_died(self, mode: str) -> bool:
        '''Check if snake dashed boundaries or hurt itself.'''
        return self.__is_limited(mode) and self.__is_dash() or self.__is_hurt()

    def __is_limited(self, mode: str) -> bool:
        '''Check if mode is limited.'''
        return mode == 'LIMITED' or self.__reverse()

    def __reverse(self) -> None:
        '''Reverse co-ordinate if snake touched sides of boder.'''
        if not (0 <= self.__lead.x < self.__dim.x):
            self.__lead.x = self.__dim.x - self.__size if self.__lead.x < 0 else 0
        if not (0 <= self.__lead.y < self.__dim.y):
            self.__lead.y = self.__dim.y - self.__size if self.__lead.y < 0 else 0

    def __is_dash(self) -> bool:
        '''Check if snake dashed boundaries.'''
        return not (0 <= self.__lead.x < self.__dim.x and 0 <= self.__lead.y < self.__dim.y)

    def __is_hurt(self) -> bool:
        '''Check if snake hurt itself.'''
        return self.__lead in self.__body[1:]

# DISPLAY.
    def draw(self) -> None:
        '''Draw snake object.'''
        self.__screen.blit(self.__get_head(), self.__body[0])
        for i in range(1, len(self.__body) - 1):
            self.__screen.blit(self.__get_body(i), self.__body[i])
        self.__screen.blit(self.__get_tail(), self.__body[-1])

    def __get_head(self) -> None:
        '''Get image of head.'''
        match self.__direction:
            case 'L':
                return self.__images[0][0]
            case 'R':
                return self.__images[0][1]
            case 'U':
                return self.__images[0][2]
            case 'D':
                return self.__images[0][3]

    def __get_body(self, index: int) -> None:
        '''Get image of body.'''
        prev = self.__body[index - 1] - self.__body[index]
        next = self.__body[index + 1] - self.__body[index]
        # VERTICAL, HORIZONTAL, WINDING & CORNER CASES.
        if prev.x == next.x:
            return self.__images[1][0]
        elif prev.y == next.y:
            return self.__images[1][1]
        else:
            if prev.y == -self.__size and next.x == -self.__size \
                    or prev.x == -self.__size and next.y == -self.__size:
                return self.__images[1][2]
            elif prev.y == self.__size and next.x == -self.__size \
                    or prev.x == -self.__size and next.y == self.__size:
                return self.__images[1][3]
            elif prev.y == -self.__size and next.x == self.__size \
                    or prev.x == self.__size and next.y == -self.__size:
                return self.__images[1][4]
            elif prev.y == self.__size and next.x == self.__size \
                    or prev.x == self.__size and next.y == self.__size:
                return self.__images[1][5]
            else:
                return self.__check_corners(prev, next)

    def __get_tail(self) -> None:
        '''Get image of tail.'''
        link = self.__body[-2] - self.__body[-1]
        # INSIDE & OUTSIDE CASES.
        if link.x == -self.__size or link.x > self.__size:
            return self.__images[2][0]
        elif link.x == self.__size or link.x < -self.__size:
            return self.__images[2][1]
        elif link.y == -self.__size or link.y > self.__size:
            return self.__images[2][2]
        elif link.y == self.__size or link.y < -self.__size:
            return self.__images[2][3]

    def __check_corners(self, a: Vector2, b: Vector2) -> None:
        '''Check if snake shifted in special corners.'''
        # FROM INSIDE TO OUTSIDE, OUTSIDE TO INSIDE & CORNERS OF GROUNDPLAY.
        if a.y > self.__size and b.x == -self.__size or a.x > self.__size and b.y == -self.__size \
            or a.y == -self.__size and b.x > self.__size or a.x == -self.__size and b.y > self.__size \
                or a.y > self.__size and b.x > self.__size or a.x > self.__size and b.y > self.__size:
            return self.__images[1][2]
        elif a.y < -self.__size and b.x == -self.__size or a.x > self.__size and b.y == self.__size \
            or a.y == self.__size and b.x > self.__size or a.x == -self.__size and b.y < -self.__size \
                or a.y < -self.__size and b.x > self.__size or a.x > self.__size and b.y < -self.__size:
            return self.__images[1][3]
        elif a.y > self.__size and b.x == self.__size or a.x < -self.__size and b.y == -self.__size \
            or a.y == -self.__size and b.x < -self.__size or a.x == self.__size and b.y > self.__size \
                or a.y > self.__size and b.x < -self.__size or a.x < -self.__size and b.y > self.__size:
            return self.__images[1][4]
        elif a.y < -self.__size and b.x == self.__size or a.x < -self.__size and b.y == self.__size \
            or a.y == self.__size and b.x < -self.__size or a.x == self.__size and b.y < -self.__size \
                or a.y < -self.__size and b.x < -self.__size or a.x < -self.__size and b.y < -self.__size:
            return self.__images[1][5]
