from random import randint
from sys import exit

import pygame as pg


class Tree(pg.sprite.Sprite):

    def __init__(self, place, group):
        super().__init__(group)
        # CORE.
        self.image = pg.image.load('image/TREE.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=place)


class Player(pg.sprite.Sprite):

    def __init__(self, place, group):
        super().__init__(group)
        # CORE.
        self.image = pg.image.load('image/PLAYER.png').convert_alpha()
        self.rect = self.image.get_rect(center=place)
        # MOVEMENT.
        self.direction, self.speed = pg.math.Vector2(), 5

    def input(self):
        '''Inputting.'''
        keys = pg.key.get_pressed()
        # HORIZONTAL.
        if keys[pg.K_LEFT]:
            self.direction.x = -1
        elif keys[pg.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0
        # VERTICAL.
        if keys[pg.K_UP]:
            self.direction.y = -1
        elif keys[pg.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

    def update(self):
        '''Updating.'''
        self.input()
        self.rect.center += self.direction * self.speed


class OYSortCamera(pg.sprite.Group):
    '''
    CAMERA DISPLAYS SPRITES BASED ON THEIR Y-ORDINATE.\n
    THE HIGHER Y-ORDINATE WOULD APPEAR IN FRONT OF THE LOWER.
    '''

    def __init__(self):
        super().__init__()
        # CORE.
        self.screen = pg.display.get_surface()
        self.ground = pg.image.load('image/GROUND.png').convert_alpha()

    def draws(self):
        '''CUSTOMIZED DRAW.'''
        # BACKGROUND.
        self.screen.blit(self.ground, (0, 0))
        # ENTITY.
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            self.screen.blit(sprite.image, sprite.rect)


class CenterCamera(pg.sprite.Group):
    '''
    CAMERA DISPLAYS SPRITES BASED ON THE CO-ORDINATE OF THE PLAYER.\n
    THE PLAYER WOULD BE ALWAYS IN THE CENTER OF THE SCREEN.
    '''

    def __init__(self):
        super().__init__()
        # CORE.
        self.screen = pg.display.get_surface()
        self.ground = pg.image.load('image/GROUND.png').convert_alpha()
        # OFFSET.
        self.offset = pg.math.Vector2()

    def draws(self, player: Player):
        '''CUSTOMIZED DRAW.'''
        # UPDATE OFFSET.
        self.offset.update(player.rect.centerx - DIMENSION[0] / 2,
                           player.rect.centery - DIMENSION[1] / 2)
        # BACKGROUND.
        self.screen.blit(self.ground, -self.offset)
        # ENTITY.
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.screen.blit(sprite.image, offset_rect)


class BoxFormCamera(pg.sprite.Group):
    '''
    CAMERA DISPLAYS SPRITES BASED ON THE BOX RECT SURROUNDING THE PLAYER.\n
    THE BOX RECT WOULD BE CHANGED IF THE PLAYER MOVES OUT OF THE BOX AREA.
    '''

    def __init__(self):
        super().__init__()
        # CORE.
        self.screen = pg.display.get_surface()
        self.ground = pg.image.load('image/GROUND.png').convert_alpha()
        # OFFSET.
        self.offset = pg.math.Vector2()
        # BOX BORDER. (THE ORIGINAL DISTANCE FROM THE SCREEN TO THE BOX BODERS)
        self.box_boders = {'L': 200, 'R': 200, 'T': 100, 'B': 100}
        # BOX SETUP.
        L, T = self.box_boders['L'], self.box_boders['T']
        W = DIMENSION[0] - (self.box_boders['L'] + self.box_boders['R'])
        H = DIMENSION[1] - (self.box_boders['T'] + self.box_boders['B'])
        # BOX RECT.
        self.box_rect = pg.Rect(L, T, W, H)

    def draws(self, player: Player):
        '''CUSTOMIZED DRAW.'''
        # UPDATE BOX RECT.
        # HORIZONTAL.
        if player.rect.left < self.box_rect.left:
            self.box_rect.left = player.rect.left
        elif player.rect.right > self.box_rect.right:
            self.box_rect.right = player.rect.right
        # VERTICAL.
        if player.rect.top < self.box_rect.top:
            self.box_rect.top = player.rect.top
        elif player.rect.bottom > self.box_rect.bottom:
            self.box_rect.bottom = player.rect.bottom
        # UPDATE OFFSET.
        self.offset.update(self.box_rect.left - self.box_boders['L'],
                           self.box_rect.top - self.box_boders['T'])
        # BACKGROUND.
        self.screen.blit(self.ground, -self.offset)
        # ENTITY.
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.screen.blit(sprite.image, offset_rect)


class ControlCamera(pg.sprite.Group):
    '''
    CAMERA DISPLAYS SPRITES BASED ON THE OFFSET.\n
    THE OFFSET WOULD BE CHANGED VIA KEYBOARD OR MOUSE CONTROL.
    '''

    def __init__(self):
        super().__init__()
        # CORE.
        self.screen = pg.display.get_surface()
        self.ground = pg.image.load('image/GROUND.png')
        # OFFSET.
        self.offset = pg.math.Vector2()
        # SETUP.
        # self.SETUP_KEYBOARD()
        self.SETUP_MOUSE()

    def SETUP_KEYBOARD(self):
        '''KEYBOARD ATTRIBUTES.'''
        self.CAMERA_SPEED = 5

    def CONTROL_KEYBOARD(self):
        '''KEYBOARD CONTROLLER.'''
        keys = pg.key.get_pressed()
        # UPDATE OFFSET.
        # HORIZONTAL.
        if keys[pg.K_a]:
            self.offset.x -= self.CAMERA_SPEED
        elif keys[pg.K_d]:
            self.offset.x += self.CAMERA_SPEED
        # VERTICAL.
        if keys[pg.K_w]:
            self.offset.y -= self.CAMERA_SPEED
        elif keys[pg.K_s]:
            self.offset.y += self.CAMERA_SPEED

    def SETUP_MOUSE(self):
        '''MOUSE ATTRIBUTES.'''
        # BOX BORDER. (THE ORIGINAL DISTANCE FROM THE SCREEN TO THE BOX BODERS)
        self.box_boders = {'L': 200, 'R': 200, 'T': 100, 'B': 100}
        # BOX SETUP.
        self.L_BODER, self.T_BODER = self.box_boders['L'], self.box_boders['T']
        self.R_BODER = DIMENSION[0] - self.box_boders['R']
        self.B_BODER = DIMENSION[1] - self.box_boders['B']
        # CAMERA SPEED.
        self.CAMERA_SPEED = 0.5

    def CONTROL_MOUSE(self):
        '''MOUSE CONTROLLER.'''
        # MOUSE INFORMATION.
        mouse_pos = pg.math.Vector2(pg.mouse.get_pos())
        mouse_offset = pg.math.Vector2()
        # UPDATE MOUSE OFFSET.
        # HORIZONTAL.
        if self.T_BODER < mouse_pos.y < self.B_BODER:
            if mouse_pos.x < self.L_BODER:
                mouse_offset.x = mouse_pos.x - self.L_BODER
                pg.mouse.set_pos(self.L_BODER, mouse_pos.y)
            elif mouse_pos.x > self.R_BODER:
                mouse_offset.x = mouse_pos.x - self.R_BODER
                pg.mouse.set_pos(self.R_BODER, mouse_pos.y)
        # HORIZONTAL & VERTICAL.
        elif mouse_pos.y < self.T_BODER:
            if mouse_pos.x < self.L_BODER:
                mouse_offset = mouse_pos - (self.L_BODER, self.T_BODER)
                pg.mouse.set_pos(self.L_BODER, self.T_BODER)
            elif mouse_pos.x > self.R_BODER:
                mouse_offset = mouse_pos - (self.R_BODER, self.T_BODER)
                pg.mouse.set_pos(self.R_BODER, self.T_BODER)
        elif mouse_pos.y > self.B_BODER:
            if mouse_pos.x < self.L_BODER:
                mouse_offset = mouse_pos - (self.L_BODER, self.B_BODER)
                pg.mouse.set_pos(self.L_BODER, self.B_BODER)
            elif mouse_pos.x > self.R_BODER:
                mouse_offset = mouse_pos - (self.R_BODER, self.B_BODER)
                pg.mouse.set_pos(self.R_BODER, self.B_BODER)
        # VERTICAL.
        if self.L_BODER < mouse_pos.x < self.R_BODER:
            if mouse_pos.y < self.T_BODER:
                mouse_offset.y = mouse_pos.y - self.T_BODER
                pg.mouse.set_pos(mouse_pos.x, self.T_BODER)
            elif mouse_pos.y > self.B_BODER:
                mouse_offset.y = mouse_pos.y - self.B_BODER
                pg.mouse.set_pos(mouse_pos.x, self.B_BODER)
        # UPDATE OFFSET.
        self.offset += mouse_offset * self.CAMERA_SPEED

    def draws(self):
        '''CUSTOMIZED DRAW.'''
        # CONTROLLER.
        # self.CONTROL_KEYBOARD()
        self.CONTROL_MOUSE()
        # BACKGROUND.
        self.screen.blit(self.ground, -self.offset)
        # ENTITY.
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.screen.blit(sprite.image, offset_rect)


class ZoomCamera(pg.sprite.Group):
    '''CAMERA COULD ZOOM IN & OUT THE MAP.'''

    def __init__(self):
        super().__init__()
        # CORE.
        self.screen = pg.display.get_surface()
        self.ground = pg.image.load('image/GROUND.png')
        # OFFSET.
        self.offset = pg.math.Vector2()
        # SETUP.
        self.SETUP_MOUSE()
        # SCALE RATE.
        self.scale = 1
        # INTERNAL SURFACE.
        self.internal_size = pg.math.Vector2(2500, 2500)
        self.internal_surf = pg.Surface(self.internal_size, pg.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(
            center=(DIMENSION[0] / 2, DIMENSION[1] / 2))
        # INTERNAL OFFSET.
        self.INTERNAL_OFFSET = pg.math.Vector2((self.internal_size[0] - DIMENSION[0]) / 2,
                                               (self.internal_size[1] - DIMENSION[1]) / 2)

    def SETUP_MOUSE(self):
        '''MOUSE ATTRIBUTES.'''
        # BOX BORDER. (THE ORIGINAL DISTANCE FROM THE SCREEN TO THE BOX BODERS)
        self.box_boders = {'L': 200, 'R': 200, 'T': 100, 'B': 100}
        # BOX SETUP.
        self.L_BODER, self.T_BODER = self.box_boders['L'], self.box_boders['T']
        self.R_BODER = DIMENSION[0] - self.box_boders['R']
        self.B_BODER = DIMENSION[1] - self.box_boders['B']
        # CAMERA SPEED.
        self.CAMERA_SPEED = 0.5

    def CONTROL_MOUSE(self):
        '''MOUSE CONTROLLER.'''
        # MOUSE INFORMATION.
        mouse_pos = pg.math.Vector2(pg.mouse.get_pos())
        mouse_offset = pg.math.Vector2()
        # UPDATE MOUSE OFFSET.
        # HORIZONTAL.
        if self.T_BODER < mouse_pos.y < self.B_BODER:
            if mouse_pos.x < self.L_BODER:
                mouse_offset.x = mouse_pos.x - self.L_BODER
                pg.mouse.set_pos(self.L_BODER, mouse_pos.y)
            elif mouse_pos.x > self.R_BODER:
                mouse_offset.x = mouse_pos.x - self.R_BODER
                pg.mouse.set_pos(self.R_BODER, mouse_pos.y)
        # HORIZONTAL & VERTICAL.
        elif mouse_pos.y < self.T_BODER:
            if mouse_pos.x < self.L_BODER:
                mouse_offset = mouse_pos - (self.L_BODER, self.T_BODER)
                pg.mouse.set_pos(self.L_BODER, self.T_BODER)
            elif mouse_pos.x > self.R_BODER:
                mouse_offset = mouse_pos - (self.R_BODER, self.T_BODER)
                pg.mouse.set_pos(self.R_BODER, self.T_BODER)
        elif mouse_pos.y > self.B_BODER:
            if mouse_pos.x < self.L_BODER:
                mouse_offset = mouse_pos - (self.L_BODER, self.B_BODER)
                pg.mouse.set_pos(self.L_BODER, self.B_BODER)
            elif mouse_pos.x > self.R_BODER:
                mouse_offset = mouse_pos - (self.R_BODER, self.B_BODER)
                pg.mouse.set_pos(self.R_BODER, self.B_BODER)
        # VERTICAL.
        if self.L_BODER < mouse_pos.x < self.R_BODER:
            if mouse_pos.y < self.T_BODER:
                mouse_offset.y = mouse_pos.y - self.T_BODER
                pg.mouse.set_pos(mouse_pos.x, self.T_BODER)
            elif mouse_pos.y > self.B_BODER:
                mouse_offset.y = mouse_pos.y - self.B_BODER
                pg.mouse.set_pos(mouse_pos.x, self.B_BODER)
        # UPDATE OFFSET.
        self.offset += mouse_offset * self.CAMERA_SPEED

    def ZOOM_KEYBOARD(self):
        '''ZOOM VIA KEYBOARD.'''
        keys = pg.key.get_pressed()
        # UPDATE SCALE.
        if keys[pg.K_q]:
            self.scale += 0.1 if self.scale < 1.5 else 0
        elif keys[pg.K_e]:
            self.scale -= 0.1 if self.scale > 0.5 else 0

    def draws(self):
        '''CUSTOMIZED DRAW.'''
        # CONTROLLER.
        self.CONTROL_MOUSE()
        # CHECK ZOOM.
        self.ZOOM_KEYBOARD()
        # BACKGROUND.
        self.internal_surf.fill('#71DDEE')
        self.internal_surf.blit(
            self.ground, self.INTERNAL_OFFSET - self.offset)
        # ENTITY.
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_rect = sprite.rect.topleft + self.INTERNAL_OFFSET - self.offset
            self.internal_surf.blit(sprite.image, offset_rect)
        # SCALED SURFACE.
        scaled_surf = pg.transform.scale(
            self.internal_surf, self.internal_size * self.scale)
        scaled_rect = scaled_surf.get_rect(
            center=(DIMENSION[0] / 2, DIMENSION[1] / 2))
        # ORIGINAL DRAW.
        self.screen.blit(scaled_surf, scaled_rect)


# SETTING.
pg.init()
DIMENSION = 1280, 720
screen = pg.display.set_mode(DIMENSION)
clock = pg.time.Clock()
# MOUSE CONTROL CAMERA. (SET UP THIS TO PREVENT THE MOUSE FROM GOING OUT SIDE OF THE SCREEN!)
pg.event.set_grab(True)

# SETUP.
all_sprites = ZoomCamera()
player = Player((720, 360), all_sprites)
for _ in range(20):
    place = randint(1000, 2000), randint(1000, 2000)
    Tree(place, all_sprites)

# MAIN LOOP.
while True:
    # EVENT.
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
        # ZOOM CAMERA (SET UP THIS TO SCROLL FOR ZOOMING!)
        if event.type == pg.MOUSEWHEEL:
            if event.y < 0:
                all_sprites.scale += event.y * 0.03 if all_sprites.scale > 0.5 else 0
            else:
                all_sprites.scale += event.y * 0.03 if all_sprites.scale < 1.5 else 0
    # OTHERS.
    screen.fill('#71DDEE')
    # UPDATE.
    all_sprites.update()
    # DRAW.
    all_sprites.draws()
    pg.display.update()
    # FPS.
    clock.tick(60)
