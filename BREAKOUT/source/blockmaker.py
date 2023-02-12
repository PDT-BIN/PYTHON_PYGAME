from os import walk

import pygame as pg


class BlockMaker:

    def __init__(self):
        # IMPORT ALL IMAGES.
        for index, (path, folders, files) in enumerate(walk('image/blocks')):
            if index != 0:
                color = path.split('\\')[-1]
                images = {file.split('.')[0]: pg.image.load(
                    f'{path}/{file}').convert_alpha() for file in files}
                self.assets[color] = images
            else:
                self.assets: dict[str, dict[str, pg.Surface]] = {
                    color: None for color in folders}

    def get_image(self, form: str, size: tuple[int, int]):
        # INFORMATION.
        image = pg.Surface(size, flags=pg.SRCALPHA)
        blocks = self.assets[form]

        block_size = blocks['topleft'].get_size()
        sides_size = size[0] - 2 * block_size[0], size[1] - 2 * block_size[1]

        # 4 CORNERS.
        image.blit(blocks['topleft'], (0, 0))
        image.blit(blocks['topright'], (size[0] - block_size[0], 0))
        image.blit(blocks['bottomleft'], (0, size[1] - block_size[1]))
        image.blit(blocks['bottomright'], (size[0] -
                   block_size[0], size[1] - block_size[1]))
        # 4 SIDES.
        scaled_image = pg.transform.scale(
            blocks['left'], (block_size[0], sides_size[1]))
        image.blit(scaled_image, (0, block_size[1]))

        scaled_image = pg.transform.scale(
            blocks['right'], (block_size[0], sides_size[1]))
        image.blit(scaled_image, (size[0] - block_size[0], block_size[1]))

        scaled_image = pg.transform.scale(
            blocks['top'], (sides_size[0], block_size[1]))
        image.blit(scaled_image, (block_size[0], 0))

        scaled_image = pg.transform.scale(
            blocks['bottom'], (sides_size[0], block_size[1]))
        image.blit(scaled_image, (block_size[0], size[1] - block_size[1]))

        # CENTER.
        scaled_image = pg.transform.scale(blocks['center'], sides_size)
        image.blit(scaled_image, block_size)

        return image
