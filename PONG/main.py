from math import ceil
from random import choice
from sys import exit

import pygame as pg

# BASIC SET-UP.
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
pg.mixer.pre_init()
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Pong')

# GAME RECTANGLES.
ball = pg.Rect((SCREEN_WIDTH // 2 - 15, SCREEN_HEIGHT // 2 - 15), (30, 30))
player = pg.Rect((SCREEN_WIDTH - 20, SCREEN_HEIGHT // 2 - 70), (10, 140))
opponent = pg.Rect((10, SCREEN_HEIGHT // 2 - 70), (10, 140))

# CONSTANT STATISTIC.
BG_COLOR = pg.Color('#2F373F')
PLAYER_COLOR = 'ROYALBLUE'
LINE_COLOR = (27, 35, 43)
# DYNAMIC STATISTIC.
ball_speed_x, ball_speed_y = 7 * choice((-1, 1)), 7 * choice((-1, 1))
player_speed, opponent_speed = 0, 7

# SCORE.
player_score, opponent_score = 0, 0
game_font = pg.font.SysFont(None, 32, True)
time_font = pg.font.SysFont('inkfree', 128)
score_time = True

# SOUND.
pong_sound = pg.mixer.Sound('audio/pong.ogg')
score_sound = pg.mixer.Sound('audio/score.ogg')


def update_ball():
    global ball_speed_x, ball_speed_y, player_score, opponent_score, score_time
    # MOVEMENT.
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    if ball.left <= 0:
        player_score += 1
        score_time = pg.time.get_ticks()
        score_sound.play()
    if ball.right >= SCREEN_WIDTH:
        opponent_score += 1
        score_time = pg.time.get_ticks()
        score_sound.play()
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_speed_y *= -1
        pong_sound.play()
    # COLLISION.
    if ball.colliderect(player):
        if abs(ball.right - player.left) < 10 and ball_speed_x > 0:
            ball_speed_x *= -1
            pong_sound.play()
        elif (abs(ball.bottom - player.top) < 10 and ball_speed_y > 0 or
                abs(ball.top - player.bottom) < 10 and ball_speed_y < 0):
            ball_speed_x *= -1
            ball_speed_y *= -1
            pong_sound.play()
    if ball.colliderect(opponent):
        if abs(ball.left - opponent.right) < 10 and ball_speed_x < 0:
            ball_speed_x *= -1
            pong_sound.play()
        elif (abs(ball.bottom - opponent.top) < 10 and ball_speed_y > 0 or
                abs(ball.top - opponent.bottom) < 10 and ball_speed_y < 0):
            ball_speed_x *= -1
            ball_speed_y *= -1
            pong_sound.play()


def update_player():
    # MOVEMENT.
    player.y += player_speed
    # COLLISION.
    if player.top <= 0:
        player.top = 0
    if player.bottom >= SCREEN_HEIGHT:
        player.bottom = SCREEN_HEIGHT


def update_opponent():
    # MOVEMENT.
    if opponent.top < ball.centery:
        opponent.top += opponent_speed
    if opponent.bottom > ball.centery:
        opponent.bottom -= opponent_speed
    # COLLISION.
    if opponent.top <= 0:
        opponent.top = 0
    if opponent.bottom >= SCREEN_HEIGHT:
        opponent.bottom = SCREEN_HEIGHT


def restart_game():
    global ball_speed_x, ball_speed_y, score_time
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    current_time = pg.time.get_ticks()
    if current_time - score_time <= 5000:
        countdown = ceil((score_time - current_time) // 1000) + 5
        if countdown > 3:
            time_text = time_font.render('READY!', True, 'CRIMSON')
        elif countdown > 0:
            time_text = time_font.render(str(countdown), True, 'CRIMSON')
        else:
            time_text = time_font.render('GO!', True, 'CRIMSON')
        time_rect = time_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(time_text, time_rect)
        ball_speed_x = 0
        ball_speed_y = 0
    else:
        ball_speed_x = 7 * choice((-1, 1))
        ball_speed_y = 7 * choice((-1, 1))
        score_time = None


def handle_event():
    global player_speed
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                player_speed -= 7
            if event.key == pg.K_DOWN:
                player_speed += 7
        if event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                player_speed += 7
            if event.key == pg.K_DOWN:
                player_speed -= 7


def draw_screen():
    screen.fill(BG_COLOR)
    pg.draw.rect(screen, PLAYER_COLOR, player)
    pg.draw.rect(screen, LINE_COLOR, opponent)
    pg.draw.ellipse(screen, LINE_COLOR, ball)
    pg.draw.aaline(screen, LINE_COLOR, (SCREEN_WIDTH // 2, 0),
                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    player_text = game_font.render(str(player_score), True, LINE_COLOR)
    screen.blit(player_text, (660, 350))
    opponent_text = game_font.render(str(opponent_score), True, LINE_COLOR)
    screen.blit(opponent_text, (607, 350))


# MAIN LOOP.
while True:
    # HANDLE EVENT.
    handle_event()
    # UPDATE INDICATOR.
    update_ball()
    update_player()
    update_opponent()
    # DRAW OBJECT.
    draw_screen()
    if score_time:
        restart_game()
    # UPDATE THE FRAME.
    pg.display.update()
    # LIMIT THE FRAMES PER SECOND.
    clock.tick(60)
