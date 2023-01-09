from enitity import Entity
from player import Player
from pygame.mask import from_surface
from pygame.math import Vector2
from pygame.sprite import Group


class Monster:
    '''A class to be inherited by Coffin & Cactus.'''

    def notice(self):
        '''Check the distance & direction between Player & Enemy.'''
        # Get positions.
        stats = Vector2(self.player.rect.center) - Vector2(self.rect.center)
        # Calculate distance & direction.
        distance = stats.magnitude()
        direction = stats.normalize() if distance != 0 else Vector2()
        return distance, direction

    def confront(self):
        '''Face to the player.'''
        distance, direction = self.notice()
        if distance < self.notice_radius:
            if -0.5 < direction.y < 0.5:
                if direction.x < 0:
                    self.status = 'left_idle'
                elif direction.x > 0:
                    self.status = 'right_idle'
            else:
                if direction.y < 0:
                    self.status = 'up_idle'
                elif direction.y > 0:
                    self.status = 'down_idle'

    def approach(self):
        '''Walk to the player.'''
        distance, direction = self.notice()
        if self.attack_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split('_')[0]
        else:
            self.direction = Vector2()


class Coffin(Entity, Monster):
    '''A class to manage Coffin monster.'''

    def __init__(self, position: tuple, groups: Group, image_path: str, obstacles: Group, player: Player):
        '''Initialize core attributes.'''
        super().__init__(position, groups, image_path, obstacles)
        # Overwrite.
        self.speed = 150
        # Aim.
        self.player = player
        # Interactive attributes.
        self.notice_radius = 550
        self.walk_radius = 400
        self.attack_radius = 50

    def attack(self):
        '''Attack the player.'''
        distance = self.notice()[0]
        # Check if the Coffin could attack.
        if distance < self.attack_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0
        # Change status to attacking status.
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def animate(self, dt: float):
        '''Animate the enemy.'''
        current_animation = self.animations[self.status]
        self.frame_index += 7 * dt
        # Attacking time.
        if self.attacking and int(self.frame_index) == 4:
            if self.notice()[0] < self.attack_radius:
                self.player.damage()
        # Animation.
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        self.image = current_animation[int(self.frame_index)]
        self.mask = from_surface(self.image)

    def update(self, delta_time: float):
        '''Update all activities.'''
        self.confront()
        self.approach()
        self.attack()
        self.move(delta_time)
        self.animate(delta_time)
        self.blink()
        self.vulnerability_timer()
        self.check_death()


class Cactus(Entity, Monster):
    '''A class to manage Cactus monster.'''

    def __init__(self, position: tuple, groups: Group, image_path: str, obstacles: Group,
                 player: Player, shoot_method):
        '''Initialize core attributes.'''
        super().__init__(position, groups, image_path, obstacles)
        # Overwrite.
        self.speed = 90
        # Aim.
        self.player = player
        # Interactive attributes.
        self.notice_radius = 600
        self.walk_radius = 500
        self.attack_radius = 350
        # Shooting.
        self.shoot = shoot_method
        self.is_shot = False

    def attack(self):
        '''Attack the player.'''
        distance = self.notice()[0]
        # Check if the Cactus could attack.
        if distance < self.attack_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0
            self.is_shot = False
        # Change status to attacking status.
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def animate(self, dt: float):
        '''Animate the enemy.'''
        current_animation = self.animations[self.status]
        self.frame_index += 7 * dt
        # Attacking time.
        if self.attacking and int(self.frame_index) == 7 and not self.is_shot:
            direction = self.notice()[1]
            bullet_offset = self.rect.center + direction * 80
            self.shoot(bullet_offset, direction)
            self.is_shot = True
            self.shoot_sound.play()
        # Animation.
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        self.image = current_animation[int(self.frame_index)]
        self.mask = from_surface(self.image)

    def update(self, delta_time: float):
        '''Update all activities.'''
        self.confront()
        self.approach()
        self.attack()
        self.move(delta_time)
        self.animate(delta_time)
        self.blink()
        self.vulnerability_timer()
        self.check_death()
