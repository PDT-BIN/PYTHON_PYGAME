from random import randint

from groups import WorldSprite
from pytmx import TiledMap, TiledObject
from settings import *
from sprites import AnimatedSprite, Icon, Node, Path, Sprite
from statistic import Data


class Overworld:
    def __init__(
        self,
        tmx_map: TiledMap,
        overworld_frames: Asset,
        data: Data,
        switch_stage: Callable[[str, int], None],
    ):
        self.screen = pg.display.get_surface()
        self.data = data
        self.switch_stage = switch_stage
        # GROUP.
        self.all_sprite = WorldSprite(data)
        self.group_node: Sequence[Node] = pg.sprite.Group()
        self.load_data(tmx_map, overworld_frames)
        # STATE.
        self.current_node: Node = [e for e in self.group_node if e.level == 0][0]
        # REUSABLE FRAME.
        self.frames_path = overworld_frames["path"]
        # BUILD PATH BETWEEN NODE.
        self.create_path()

    def load_data(self, tmx_map: TiledMap, overworld_frames: Asset):
        # TILE SPRITE.
        for layer in ("main", "top"):
            for x, y, surface in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surface,
                    self.all_sprite,
                    Z_LAYERS["BG TILES"],
                )
        # WATER SPRITE.
        for row in range(tmx_map.width):
            for col in range(tmx_map.height):
                AnimatedSprite(
                    (col * TILE_SIZE, row * TILE_SIZE),
                    overworld_frames["water"],
                    self.all_sprite,
                    Z_LAYERS["BG"],
                )
        # OBJECTS.
        for instance in tmx_map.get_layer_by_name("Objects"):
            instance: TiledObject

            name = instance.name
            position = instance.x, instance.y
            # ANIMATED SPRITE.
            if name == "palm":
                AnimatedSprite(
                    position,
                    overworld_frames["palms"],
                    self.all_sprite,
                    animation_speed=randint(4, 6),
                )
            # STATIC SPRITE.
            else:
                z_index = (
                    Z_LAYERS["BG TILES"] if name == "stone" else Z_LAYERS["BG DETAILS"]
                )
                Sprite(position, instance.image, self.all_sprite, z_index)
        # PATH. (KEY: END POINT, VALUE: START POINT & PATH FROM START TO END)
        self.paths = {}
        for instance in tmx_map.get_layer_by_name("Paths"):
            self.paths[instance.properties["end"]] = {
                "start": instance.properties["start"],
                "points": [
                    (point.x + TILE_SIZE / 2, point.y + TILE_SIZE / 2)
                    for point in instance.points
                ],
            }
        # NODE & PLAYER.
        for instance in tmx_map.get_layer_by_name("Nodes"):
            instance: TiledObject

            name = instance.name
            position = instance.x + TILE_SIZE / 2, instance.y + TILE_SIZE / 2
            if name == "Node":
                available_paths = {
                    key: value
                    for key, value in instance.properties.items()
                    if key != "stage"
                }
                Node(
                    position,
                    overworld_frames["path"]["node"],
                    (self.all_sprite, self.group_node),
                    instance.properties["stage"],
                    self.data,
                    available_paths,
                )
                # PLAYER.
                if instance.properties["stage"] == self.data.current_level:
                    self.icon = Icon(
                        position, overworld_frames["icon"], self.all_sprite
                    )

    # ORIGINAL SOLUTION.
    # def create_path(self):
    #     # BUILD PATH TILE
    #     nodes = {node.level: node.grid_pos for node in self.group_node}
    #     path_tiles = {}
    #     for target, data in self.paths.items():
    #         start_node = nodes[data["start"]]
    #         path = data["points"]
    #         # BUILD A PATH FROM START NODE TO END NODE.
    #         path_tiles[target] = [start_node]
    #         for index, point in enumerate(path):
    #             if index < len(path) - 1:
    #                 start, end = Vector2(point), Vector2(path[index + 1])
    #                 # TILE QUANTITY FROM START TO END.
    #                 tiles = (end - start) / TILE_SIZE
    #                 # CONVERT CENTER POSITION TO TOPLEFT GRID POSITION.
    #                 start_tile = int(start.x / TILE_SIZE), int(start.y / TILE_SIZE)
    #                 # VERTICAL DIRECTION.
    #                 if tiles.y:
    #                     direction = 1 if tiles.y > 0 else -1
    #                     for y in range(direction, int(tiles.y) + direction, direction):
    #                         path_tiles[target].append(start_tile + Vector2(0, y))
    #                 # HORIZONTAL DIRECTION.
    #                 if tiles.x:
    #                     direction = 1 if tiles.x > 0 else -1
    #                     for x in range(direction, int(tiles.x) + direction, direction):
    #                         path_tiles[target].append(start_tile + Vector2(x, 0))
    #     # BUILD PATH SPRITE.
    #     for target, path in path_tiles.items():
    #         for index, tile in enumerate(path):
    #             if 0 < index < len(path) - 1:
    #                 prev_tile = path[index - 1] - tile
    #                 next_tile = path[index + 1] - tile
    #                 # CHECK RELATIONSHIP.
    #                 if prev_tile.x == next_tile.x:
    #                     surface = self.frames_path["vertical"]
    #                 elif prev_tile.y == next_tile.y:
    #                     surface = self.frames_path["horizontal"]
    #                 else:
    #                     if (prev_tile.y == -1 and next_tile.x == 1) or (
    #                         prev_tile.x == 1 and next_tile.y == -1
    #                     ):
    #                         surface = self.frames_path["bl"]
    #                     if (prev_tile.y == -1 and next_tile.x == -1) or (
    #                         prev_tile.x == -1 and next_tile.y == -1
    #                     ):
    #                         surface = self.frames_path["br"]
    #                     if (prev_tile.y == 1 and next_tile.x == 1) or (
    #                         prev_tile.x == 1 and next_tile.y == 1
    #                     ):
    #                         surface = self.frames_path["tl"]
    #                     if (prev_tile.y == 1 and next_tile.x == -1) or (
    #                         prev_tile.x == -1 and next_tile.y == 1
    #                     ):
    #                         surface = self.frames_path["tr"]
    #                 Path(tile * TILE_SIZE, surface, self.all_sprite, target)

    # MY SOLUTION.
    def create_path(self):
        # BUILD PATH TILE.
        path_tiles = {}
        for target, data in self.paths.items():
            # CONVERT PIXEL POINTS TO GRID POINTS.
            grid_points = [
                Vector2(int(point[0] / TILE_SIZE), int(point[1] / TILE_SIZE))
                for point in data["points"]
            ]
            # STORE THE START POINT.
            path_tiles[target] = [grid_points[0]]
            # STORE THE REST POINTS.
            for index, point in enumerate(grid_points):
                if index < len(grid_points) - 1:
                    start, end = point, grid_points[index + 1]
                    tiles = end - start
                    # VERTICAL PATH.
                    if tiles.y:
                        direction = 1 if tiles.y > 0 else -1
                        path_tiles[target].extend(
                            [
                                start + (0, y)
                                for y in range(
                                    direction, int(tiles.y) + direction, direction
                                )
                            ]
                        )
                    # HORIZONTAL PATH.
                    else:
                        direction = 1 if tiles.x > 0 else -1
                        path_tiles[target].extend(
                            [
                                start + (x, 0)
                                for x in range(
                                    direction, int(tiles.x) + direction, direction
                                )
                            ]
                        )
        # BUILD PATH SPRITE.
        for target, path in path_tiles.items():
            for index, tile in enumerate(path):
                if 0 < index < len(path) - 1:
                    prev_tile = path[index - 1] - tile
                    next_tile = path[index + 1] - tile
                    # CHECK RELATIONSHIP.
                    if prev_tile.x == next_tile.x:
                        surface = self.frames_path["vertical"]
                    elif prev_tile.y == next_tile.y:
                        surface = self.frames_path["horizontal"]
                    else:
                        if (prev_tile.y == -1 and next_tile.x == 1) or (
                            prev_tile.x == 1 and next_tile.y == -1
                        ):
                            surface = self.frames_path["bl"]
                        if (prev_tile.y == -1 and next_tile.x == -1) or (
                            prev_tile.x == -1 and next_tile.y == -1
                        ):
                            surface = self.frames_path["br"]
                        if (prev_tile.y == 1 and next_tile.x == 1) or (
                            prev_tile.x == 1 and next_tile.y == 1
                        ):
                            surface = self.frames_path["tl"]
                        if (prev_tile.y == 1 and next_tile.x == -1) or (
                            prev_tile.x == -1 and next_tile.y == 1
                        ):
                            surface = self.frames_path["tr"]
                    Path(tile * TILE_SIZE, surface, self.all_sprite, target)

    def input(self):
        """HANDLE INPUT"""
        # DON'T HANDLE WHEN PLAYER IS MOVING.
        if not self.icon.path and self.current_node:
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] and self.current_node.can_move("left"):
                self.move("left")
            if keys[pg.K_RIGHT] and self.current_node.can_move("right"):
                self.move("right")
            if keys[pg.K_UP] and self.current_node.can_move("up"):
                self.move("up")
            if keys[pg.K_DOWN] and self.current_node.can_move("down"):
                self.move("down")
            if keys[pg.K_RETURN]:
                self.data.current_level = self.current_node.level
                self.switch_stage("LEVEL")

    def move(self, direction: str):
        """HANDLE MOVE BETWEEN NODES"""
        # GET THE TARGET NODE.
        path_key = int(self.current_node.paths[direction][0])
        # CHECK IF GO BACK INSTEAD OF GO TO.
        path_reverse = self.current_node.paths[direction][-1] == "r"
        # GET THE PATH.
        points = self.paths[path_key]["points"]
        path = points if not path_reverse else points[::-1]
        # MOVE TO THE TARGET NODE.
        self.icon.start_move(path)

    def check_current_node(self):
        """GET THE NODE THAT THE PLAYER IS STANDING"""
        if not self.icon.direction:
            self.current_node = pg.sprite.spritecollide(
                self.icon, self.group_node, False
            )[0]

    def run(self, delta_time: float):
        self.screen.fill("BLACK")
        self.input()
        self.all_sprite.update(delta_time)
        self.check_current_node()
        self.all_sprite.draw(self.icon.rect.center)
