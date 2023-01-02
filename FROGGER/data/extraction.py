import pygame, sys
from pytmx.util_pygame import load_pygame
pygame.init()
screen = pygame.display.set_mode((1280,720))

tmx_data = load_pygame('map.tmx')
layer = tmx_data.get_layer_by_name('Game Objects')
for obj in layer:
	if obj.name == 'light_wooden':
		print(f'({obj.x},{obj.y})')
	# print(obj.x)
	# print(obj.y)
	# print(obj.name)