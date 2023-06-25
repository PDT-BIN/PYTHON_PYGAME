from collections.abc import Callable, Sequence
from random import choice, randint
from sys import exit

import pygame as pg
from canvas import CanvasObject, CanvasTile
from menu import Menu
from pygame import Surface
from pygame.event import Event
from pygame.key import get_pressed as key_pressed
from pygame.math import Vector2 as Vector
from pygame.mouse import get_pos as mouse_pos
from pygame.mouse import get_pressed as mouse_pressed
from pygame.sprite import Group
from settings import *
from supports import *
from timers import Timer


class Editor:
    def __init__(self, land_tiles: dict[str, Surface], switch: Callable[[dict[str, dict] | None], None]):
        self.screen = pg.display.get_surface()
        # CONTROL SYSTEM.
        self.switch = switch
        # CONTROL SCREEN.
        self.origin = Vector()
        self.pan_active = False
        self.pan_offset = Vector()
        # CONTROL GRID.
        self.grid = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.grid.set_colorkey('GREEN')
        self.grid.set_alpha(30)
        # RESOURCE.
        self.land_tiles = land_tiles
        self.upload_data()
        # CONTROL CLOUDS. ({'Surface', 'Position', 'Speed'})
        self.clouds: list[dict[str, Surface | tuple[int, int] | int]] = []
        self.startup_cloud()
        self.cloud_timer = pg.USEREVENT + 1
        pg.time.set_timer(self.cloud_timer, 2000)
        # CONTROL CANVAS. ({'Position', 'Tile'})
        self.canvas_data: dict[tuple[int, int], CanvasTile] = {}
        self.last_selected_cell: tuple[int, int] = None
        # CONTROL MENU.
        self.menu = Menu()
        self.choice = 2
        # OBJECTS SYSTEM.
        self.canvas_objects: Sequence[CanvasObject] = Group()
        self.bg_objects: Sequence[CanvasObject] | Group = Group()
        self.fg_objects: Sequence[CanvasObject] | Group = Group()
        self.drag_active = False
        self.object_timer = Timer(500)
        # DEPENDENT OBJECT. (PLAYER & SKY HANDLE)
        self.player = CanvasObject((self.canvas_objects, self.fg_objects), 0, self.animations[0]['frames'],
                                   self.origin, (200, WINDOW_HEIGHT / 2))
        self.sky_handle = CanvasObject((self.canvas_objects, self.bg_objects), 1, [self.sky_handle_surf],
                                       self.origin, (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        # MUSIC & SOUND.
        self.music = pg.mixer.Sound('audio/Explorer.ogg')
        self.music.set_volume(0.4)
        self.music.play(loops=-1)

    def upload_data(self):
        # DEPENDENT TILE.
        self.water_surf = load_an_image('image/terrain/water/water_bottom.png')
        self.sky_handle_surf = load_an_image('image/cursors/handle.png')
        self.cloud_surfs = load_folder_list('image/clouds')
        # IMAGE.
        self.animations: dict[int, dict[str, int | list[Surface]]] = {}
        self.previews: dict[int, Surface] = {}
        for key, value in EDITOR_DATA.items():
            # ANIMATION.
            if value['graphics']:
                graphics = load_folder_list(value['graphics'])
                self.animations[key] = {
                    'frame index': 0, 'frames': graphics, 'length': len(graphics)}
            # PREVIEW.
            if value['preview']:
                self.previews[key] = load_an_image(value['preview'])

    # CANVAS.
    def update_animation(self, delta_time: float):
        for value in self.animations.values():
            value['frame index'] += ANIMATION_SPEED * delta_time
            if value['frame index'] >= len(value['frames']):
                value['frame index'] = 0

    def get_selected_cell(self, obj: CanvasObject = None) -> tuple[int, int]:
        # CALCULATE DISTANCE FROM MOUSE/OBJECT POSITION TO ORIGIN POINT.
        distance_to_origin: Vector = (mouse_pos() - self.origin) \
            if not obj else obj.distance_to_origin
        # CALCULATE (X,Y) OF CELL IN GIRD (A INFINITE-2D MATRIX).
        return (int(distance_to_origin.x / TILE_SIZE) - (distance_to_origin.x < 0),
                int(distance_to_origin.y / TILE_SIZE) - (distance_to_origin.y < 0))

    def check_neighbors(self, tile_pos: tuple[int, int]):
        # CREATE A LOCAL CLUSTER.
        size = 3
        local_cluster = [(tile_pos[0] + col - int(size / 2), tile_pos[1] + row - int(size / 2))
                         for col in range(size) for row in range(size)]
        # CHECK NEIGHBORS.
        for cell in filter(lambda cell: cell in self.canvas_data, local_cluster):
            # RESET ATTRIBUTES OF TILE.
            self.canvas_data[cell].terrain_neighbors.clear()
            self.canvas_data[cell].water_on_top = False
            # CHECK TILES SURROUNDING THIS NEIGHBOR.
            for name, side in NEIGHBOR_DIRECTIONS.items():
                neighbor_cell = cell[0] + side[0], cell[1] + side[1]
                if neighbor_cell in self.canvas_data:
                    # WATER ON TOP.
                    if name == 'A' and self.canvas_data[cell].has_water \
                            and self.canvas_data[neighbor_cell].has_water:
                        self.canvas_data[cell].water_on_top = True
                    # TERRAIN NEIGHBORS.
                    if self.canvas_data[neighbor_cell].has_terrain:
                        self.canvas_data[cell].terrain_neighbors.append(name)

    def get_selected_object(self) -> CanvasObject:
        for sprite in self.canvas_objects:
            if sprite.rect.collidepoint(mouse_pos()):
                return sprite

    def export_layers(self) -> dict[str, dict[tuple[int, int], str | int]]:
        # REMOVE ALL OBJECTS FROM TILE.
        for tile in self.canvas_data.values():
            tile.objects.clear()
        # LINK OBJECT TO CANVAS DATA.
        for obj in self.canvas_objects:
            link_cell = self.get_selected_cell(obj)
            offset = obj.distance_to_origin - Vector(link_cell) * TILE_SIZE
            # CHECK EXIST TILE.
            if link_cell in self.canvas_data:
                self.canvas_data[link_cell].add_id(obj.tile_id, offset)
            else:
                self.canvas_data[link_cell] = CanvasTile(obj.tile_id, offset)
        # LAYERS OF LEVEL.
        layers: dict[str, dict[tuple[int, int], str | int]] = {
            'water': {},    'bg palms': {}, 'terrain': {},
            'enemies': {},  'coins': {},    'fg objects': {}
        }
        # GRID OFFSET. (THE TOPLEFT BECOMES THE (0,0))
        x_offset = min(self.canvas_data.keys(), key=lambda pos: pos[0])[0]
        y_offset = min(self.canvas_data.keys(), key=lambda pos: pos[1])[1]
        # FILL THE LAYERS.
        for tile_pos, tile_data in self.canvas_data.items():
            new_pos = ((tile_pos[0] - x_offset) * TILE_SIZE,
                       (tile_pos[1] - y_offset) * TILE_SIZE)
            # FILL DATA.
            if tile_data.has_water:
                layers['water'][new_pos] = tile_data.get_water_type()

            if tile_data.has_terrain:
                layers['terrain'][new_pos] = tile_data.get_terrain_type(
                    self.land_tiles)

            if tile_data.coin:
                layers['coins'][new_pos] = tile_data.coin

            if tile_data.enemy:
                layers['enemies'][new_pos] = tile_data.enemy

            if tile_data.objects:
                for tile_id, offset in tile_data.objects:
                    offset_pos = (new_pos[0] + offset.x, new_pos[1] + offset.y)
                    if EDITOR_DATA[tile_id]['style'] == 'palm_bg':
                        layers['bg palms'][offset_pos] = tile_id
                    else:
                        layers['fg objects'][offset_pos] = tile_id
        return layers

    def target_player(self):
        # DETERMINE THE ORIGIN POINT VIA PLAYER.
        HALF_SCREEN = Vector(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        ratio = Vector(int(self.player.distance_to_origin.x / HALF_SCREEN.x),
                       int(self.player.distance_to_origin.y / HALF_SCREEN.y))
        origin = Vector(ratio.x * HALF_SCREEN.x, ratio.y * HALF_SCREEN.y)
        # CENTER THE PLAYER.
        gap = HALF_SCREEN - (self.player.distance_to_origin - origin)
        self.origin = -origin + gap
        # PAN OBJECTS.
        for sprite in self.canvas_objects:
            sprite.pan(self.origin)
        # TARGET THE PLAYER.
        pg.mouse.set_pos(self.player.rect.center)

    # INPUT.
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                match event.key:
                    case pg.K_TAB: self.target_player()
                    case pg.K_RETURN:
                        self.switch(self.export_layers())
                        self.music.stop()
            self.input_mouse(event)
            self.input_keyboard(event)
            self.menu_event(event)
            self.drag_event(event)
            self.canvas_event()
            self.create_cloud(event)

    def input_mouse(self, event: Event):
        # CHECK MOUSE BUTTON PRESSING.
        if event.type == pg.MOUSEBUTTONDOWN and mouse_pressed()[1]:
            # CHANGE STATE.
            self.pan_active = True
            # CALCULATE OFFSET BETWEEN MOUSE AND ORIGIN.
            self.pan_offset = mouse_pos() - self.origin
        # CHANGE STATE IF NO PRESSING.
        if not mouse_pressed()[1]:
            self.pan_active = False
        # CHECK MOUSE BUTTON WHEELING.
        if event.type == pg.MOUSEWHEEL:
            # VERTICAL SCROLL IF HOLD THE 'LEFT CTRL' KEY ON KEYBOARD.
            if key_pressed()[pg.K_LCTRL]:
                self.origin.y -= event.y * TILE_SIZE
            else:
                self.origin.x -= event.y * TILE_SIZE
        # MAKE THE ORIGIN MOVE FORWARD THE MOUSE MOVEMENT.
        if self.pan_active:
            self.origin = mouse_pos() - self.pan_offset
        # OBJECTS PAN.
        if event.type == pg.MOUSEWHEEL or self.pan_active:
            for sprite in self.canvas_objects:
                sprite.pan(self.origin)

    def input_keyboard(self, event: Event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                self.choice += 1
            if event.key == pg.K_LEFT:
                self.choice -= 1
        # LIMIT THE CHOICE BETWEEN 2 AND 18.
        self.choice = max(2, min(18, self.choice))

    def menu_event(self, event: Event):
        if event.type == pg.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
            if result := self.menu.click(mouse_pos(), mouse_pressed()):
                self.choice = result

    def canvas_event(self):
        if not self.drag_active and not self.menu.rect.collidepoint(mouse_pos()):
            # GET THE POSITION OF SELECTED CELL.
            selected_cell = self.get_selected_cell()
            # CANVAS ADD.
            if mouse_pressed()[0]:
                self.canvas_add(selected_cell)
            # CANVAS DEL.
            if mouse_pressed()[2]:
                self.canvas_del(selected_cell, self.get_selected_object())

    def canvas_add(self, selected_cell: tuple[int, int]):
        if EDITOR_DATA[self.choice]['type'] == 'tile':
            if selected_cell != self.last_selected_cell:
                if selected_cell in self.canvas_data:
                    self.canvas_data[selected_cell].add_id(self.choice)
                else:
                    self.canvas_data[selected_cell] = CanvasTile(self.choice)
                # CHOOSE A RESPONSIBLE TILE AUTOMATICALLY.
                self.check_neighbors(selected_cell)
                # STORE THE PREVIOUS SELECTED CELL.
                self.last_selected_cell = selected_cell
        else:
            if not self.object_timer.is_actived:
                groups = (self.bg_objects if EDITOR_DATA[self.choice]['style'] == 'palm_bg' else self.fg_objects,
                          self.canvas_objects)
                CanvasObject(groups, self.choice,
                             self.animations[self.choice]['frames'], self.origin, mouse_pos())
                self.object_timer.activate()

    def canvas_del(self, selected_cell: tuple[int, int], selected_object: CanvasObject):
        # CHECK REMOVE OBJECT. (CAN'T REMOVE PLAYER & SKY HANDLE)
        if selected_object and selected_object.tile_id not in (0, 1):
            selected_object.kill()
        # CHECK REMOVE TILE.
        if selected_cell in self.canvas_data:
            # REMOVE ELEMENT OF TILE.
            self.canvas_data[selected_cell].del_id(self.choice)
            # REMOVE ENTIRE TILE IF NO ELEMENTS IN IT.
            if self.canvas_data[selected_cell].is_empty:
                del self.canvas_data[selected_cell]
            # CHECK ITS NEIGHBORS AFTER DELETING.
            self.check_neighbors(selected_cell)

    def drag_event(self, event: Event):
        # START DRAG.
        if event.type == pg.MOUSEBUTTONDOWN and mouse_pressed()[0]:
            for sprite in self.canvas_objects:
                if sprite.rect.collidepoint(event.pos):
                    sprite.start_drag()
                    self.drag_active = True
        # END DRAG.
        if event.type == pg.MOUSEBUTTONUP and self.drag_active:
            for sprite in self.canvas_objects:
                if sprite.is_selected:
                    sprite.end_drag(self.origin)
                    self.drag_active = False

    # DRAW.
    def draw_grid(self):
        # CALCULATE THE QUANTITY OF COLUMN & ROW ON GRID.
        cols, rows = WINDOW_WIDTH // TILE_SIZE, WINDOW_HEIGHT // TILE_SIZE
        # CALCULATE THE OFFSET BETWEEN THE ORIGIN AND THE NEXT LEFT SIDE COLUMN TO BEGIN DRAW GRID.
        origin_offset = Vector(self.origin.x - (self.origin.x // TILE_SIZE) * TILE_SIZE,
                               self.origin.y - (self.origin.y // TILE_SIZE) * TILE_SIZE)
        # FILL THE GIRD WITH ANOTHER COLOR FOR TRANSPARENTING BACKGROUND.
        self.grid.fill('GREEN')
        # DRAW THE GRID ON A DEPENDENT SURFACE.
        for col in range(cols):
            x = origin_offset.x + col * TILE_SIZE
            pg.draw.line(self.grid, LINE_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for row in range(rows):
            y = origin_offset.y + row * TILE_SIZE
            pg.draw.line(self.grid, LINE_COLOR, (0, y), (WINDOW_WIDTH, y))
        # DRAW THE GRID SURFACE ON THE SCREEN.
        self.screen.blit(self.grid, (0, 0))

    def draw_level(self):
        # BACKGROUND OBJECT.
        self.bg_objects.draw(self.screen)
        # TILE.
        for tile_pos, tile_data in self.canvas_data.items():
            grid_pos = self.origin + Vector(tile_pos) * TILE_SIZE
            # WATER.
            if tile_data.has_water:
                if tile_data.water_on_top:
                    self.screen.blit(self.water_surf, grid_pos)
                else:
                    frames = self.animations[3]['frames']
                    index = int(self.animations[3]['frame index'])
                    self.screen.blit(frames[index], grid_pos)
            # TERRAIN.
            if tile_data.has_terrain:
                terrain_name = tile_data.get_terrain_type(self.land_tiles)
                self.screen.blit(self.land_tiles[terrain_name], grid_pos)
            # COIN.
            if tile_data.coin:
                frames = self.animations[tile_data.coin]['frames']
                index = int(self.animations[tile_data.coin]['frame index'])
                surf = frames[index]
                rect = surf.get_rect(center=(grid_pos + COIN_OFFSET))
                self.screen.blit(surf, rect)
            # ENEMY.
            if tile_data.enemy:
                frames = self.animations[tile_data.enemy]['frames']
                index = int(self.animations[tile_data.enemy]['frame index'])
                surf = frames[index]
                rect = surf.get_rect(midbottom=(grid_pos + ENEMY_OFFSET))
                self.screen.blit(surf, rect)
        # FOREGROUND OBJECT.
        self.fg_objects.draw(self.screen)

    def preview(self):
        if not self.menu.rect.collidepoint(mouse_pos()):
            selected_object = self.get_selected_object()
            if selected_object:
                # DRAW INDICATOR.
                indicator = selected_object.rect.inflate(10, 10)
                color, width, length = 'BLACK', 3, 15
                # TOPLEFT.
                corner = Vector(indicator.topleft)
                pg.draw.lines(self.screen, color, closed=False, width=width,
                              points=(corner + (0, length), corner, corner + (15, 0)))
                # TOPRIGHT.
                corner = Vector(indicator.topright)
                pg.draw.lines(self.screen, color, closed=False, width=width,
                              points=(corner + (0, length), corner, corner - (15, 0)))
                # BOTTOMLEFT.
                corner = Vector(indicator.bottomleft)
                pg.draw.lines(self.screen, color, closed=False, width=width,
                              points=(corner - (0, length), corner, corner + (15, 0)))
                # BOTTOMRIGHT.
                corner = Vector(indicator.bottomright)
                pg.draw.lines(self.screen, color, closed=False, width=width,
                              points=(corner - (0, length), corner, corner - (15, 0)))
            else:
                # PREVIEW TILE/OBJECT.
                tile_type = {key: value['type']
                             for key, value in EDITOR_DATA.items()}
                surf = self.previews[self.choice].copy()
                surf.set_alpha(200)
                # TILE.
                if tile_type[self.choice] == 'tile':
                    rect = surf.get_rect(
                        topleft=self.origin + Vector(self.get_selected_cell()) * TILE_SIZE)
                # OBJECT.
                else:
                    rect = surf.get_rect(center=mouse_pos())
                self.screen.blit(surf, rect)

    def draw_sky(self, delta_time: float):
        # SKY LINE POSITION.
        sky_line = self.sky_handle.rect.centery
        # SKY BACKGROUND.
        self.screen.fill(SKY_COLOR)
        # HORIZONTAL LINES & CLOUDS.
        if sky_line > 0:
            sky_rect_bot = pg.Rect(0, sky_line - 10, WINDOW_WIDTH, 10)
            sky_rect_mid = pg.Rect(0, sky_line - 16, WINDOW_WIDTH, 4)
            sky_rect_top = pg.Rect(0, sky_line - 20, WINDOW_WIDTH, 2)
            pg.draw.rect(self.screen, HORIZON_TOP_COLOR, sky_rect_bot)
            pg.draw.rect(self.screen, HORIZON_TOP_COLOR, sky_rect_mid)
            pg.draw.rect(self.screen, HORIZON_TOP_COLOR, sky_rect_top)
            self.draw_cloud(delta_time, sky_line)
        # SEA BACKGROUND & SKY LINE.
        if 0 < sky_line < WINDOW_HEIGHT:
            pg.draw.rect(self.screen, SEA_COLOR,
                         pg.Rect(0, sky_line, WINDOW_WIDTH, WINDOW_HEIGHT - sky_line))
            pg.draw.line(self.screen, HORIZON_COLOR,
                         (0, sky_line), (WINDOW_WIDTH, sky_line), 3)
        if sky_line <= 0:
            self.screen.fill(SEA_COLOR)

    def draw_cloud(self, delta_time: float, sky_line: int):
        for cloud in self.clouds:
            # UPDATE MOVEMENT.
            cloud['pos'][0] -= cloud['speed'] * delta_time
            # DRAW CLOUD.
            position = cloud['pos'][0], sky_line - cloud['pos'][1]
            self.screen.blit(cloud['surf'], position)

    def create_cloud(self, event: Event):
        if event.type == self.cloud_timer:
            # REMOVE CLOUDS.
            self.clouds = [e for e in self.clouds if e['pos'][0] > -400]
            # ADD NEW CLOUD.
            surf = choice(self.cloud_surfs)
            pos = [WINDOW_WIDTH + randint(50, 100), randint(0, WINDOW_HEIGHT)]
            self.clouds.append({'surf': pg.transform.scale2x(surf) if randint(0, 4) < 2 else surf,
                                'pos': pos, 'speed': randint(20, 50)})

    def startup_cloud(self):
        for _ in range(10):
            surf = pg.transform.scale2x(choice(self.cloud_surfs)) \
                if randint(0, 4) < 2 else choice(self.cloud_surfs)
            pos = [randint(0, WINDOW_WIDTH - randint(100, 150)),
                   randint(0, WINDOW_HEIGHT)]
            self.clouds.append(
                {'surf': surf, 'pos': pos, 'speed': randint(20, 50)})

    # MAIN.
    def run(self, delta_time: float):
        # EVENTS.
        self.event_loop()
        # UPDATE.
        self.update_animation(delta_time)
        self.canvas_objects.update(delta_time)
        self.object_timer.update()
        # DRAW.
        self.draw_sky(delta_time)
        self.draw_level()
        self.draw_grid()
        self.preview()
        self.menu.display(self.choice)
