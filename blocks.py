from pyglet import image
from pyglet.graphics import TextureGroup

group1 = TextureGroup(image.load('textures\\blocks\\watertexture.png').get_texture())
group2 = TextureGroup(image.load('textures\\blocks\\watertexture - Copy.png').get_texture())
group3 = TextureGroup(image.load('textures\\blocks\\watertexture - Copy (2).png').get_texture())

def tex_coord(x, y, n=4):
    """ Return the bounding vertices of the texture square.
    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, front, left=None, right=None, back=None):
    """ Return a list of the texture squares for the top, bottom and side.
    """
    if not left:
        left = front
    if not right:
        right = left
    if not back:
        back = front
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    front = tex_coord(*front)
    left = tex_coord(*left)
    right = tex_coord(*right)
    back = tex_coord(*back)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(front)
    result.extend(left)
    result.extend(right)
    result.extend(back)
    return result


class Block:
    texture = tex_coords((0, 1), (0, 1), (0, 1))
    group = group1
    name = 'Block'

class Block2:
    texture = tex_coords((0, 0), (0, 0), (0, 0))
    group = group2
    name = 'Block2'

class Block3:
    texture = tex_coords((0, 0), (0, 0), (0, 0))
    group = group3
    name = 'Block3'

class GrassBlock(Block):
    texture = tex_coords((1, 0), (0, 1), (0, 0))
    name = 'Grass Block'

class Dirt(Block):
    name = 'Dirt'

class Sand(Block):
    texture = tex_coords((1, 1), (1, 1), (1, 1))
    name = 'Sand'

class Brick(Block):
    texture = tex_coords((2, 0), (2, 0), (2, 0))
    name = 'Brick'

class Stone(Block):
    texture = tex_coords((2, 1), (2, 1), (2, 1))
    name = 'Stone'

class OakWood(Block):
    texture = tex_coords((3, 1), (3, 1), (3, 1))
    name = 'Oak Wood'

class OakLeaf(Block):
    texture = tex_coords((3, 0), (3, 0), (3, 0))
    name = 'Oak Leaf'

class Water(Block):
    texture = tex_coords((0, 2), (0, 2), (0, 2))
    name = 'Water'

class BrownClay(Block):
    texture = tex_coords((1, 2), (1, 2), (1, 2))
    name = 'Brown Clay'

class SnowBlock(Block):
    texture = tex_coords((2, 2), (2, 2), (2, 2))
    name = 'Snow Block'

class OakLog(Block):
    texture = tex_coords((3, 2), (3, 2), (3, 1))
    name = 'Oak Log'

class CoalOre(Block):
    texture = tex_coords((0, 3), (0, 3), (0, 3))
    name = 'Coal Ore'

class IronOre(Block):
    texture = tex_coords((1, 3), (1, 3), (1, 3))
    name = 'Iron Ore'

class DiamondOre(Block):
    texture = tex_coords((2, 3), (2, 3), (2, 3))
    name = 'Diamond Ore'

class OakPlanks(Block):
    texture = tex_coords((3, 3), (3, 3), (3, 3))
    name = 'Oak Planks'

class GoldOre(Block2):
    texture = tex_coords((0, 3), (0, 3), (0, 3))
    name = 'Gold Ore'

class LapisOre(Block2):
    texture = tex_coords((1, 3), (1, 3), (1, 3))
    name = 'Lapis Ore'

class RedstoneOre(Block2):
    texture = tex_coords((2, 3), (2, 3), (2, 3))
    name = 'Redstone Ore'

class BirchWood(Block2):
    texture = tex_coords((3, 1), (3, 1), (3, 1))
    name = 'Birch Wood'

class BirchLog(Block2):
    texture = tex_coords((3, 2), (3, 2), (3, 1))
    name = 'Birch Log'

class BirchPlanks(Block2):
    texture = tex_coords((3, 3), (3, 3), (3, 3))
    name = 'Birch Planks'

class BirchLeaf(Block):
    texture = tex_coords((3, 0), (3, 0), (3, 0))
    name = 'Birch Leaves'

class DarkOakLog(Block2):
    texture = tex_coords((0, 2), (0, 2), (0, 1))
    name = 'Dark Oak Log'

class DarkOakPlanks(Block2):
    texture = tex_coords((0, 0), (0, 0), (0, 0))
    name = 'Dark Oak Planks'

class DarkOakWood(Block2):
    texture = tex_coords((0, 1), (0, 1), (0, 1))
    name = 'Dark Oak Wood'

class DarkOakLeaf(Block):
    texture = tex_coords((3, 0), (3, 0), (3, 0))
    name = 'Dark Oak Leaf'

class JungleLog(Block2):
    texture = tex_coords((1, 2), (1, 2), (1, 1))
    name = 'Jungle Log'

class JungleWood(Block2):
    texture = tex_coords((1, 1), (1, 1), (1, 1))
    name = 'Jungle Wood'

class JunglePlanks(Block2):
    texture = tex_coords((1, 0), (1, 0), (1, 0))
    name = 'Jungle Planks'

class JungleLeaf(Block2):
    texture = tex_coords((3, 0), (3, 0), (3, 0))
    name = 'Jungle Leaf'

class SpruceWood(Block3):
    texture = tex_coords((3, 2), (3, 2), (3, 2))
    name = 'Spruce Wood'

class SpruceLog(Block3):
    texture = tex_coords((3, 2), (3, 2), (3, 1))
    name = 'Spruce Log'

class SprucePlanks(Block3):
    texture = tex_coords((3, 3), (3, 3), (3, 3))
    name = 'Spruce Planks'

class SpruceLeaf(Block):
    texture = tex_coords((3, 0), (3, 0), (3, 0))
    name = 'Spruce Leaf'

class AcaciaLog(Block2):
    texture = tex_coords((2, 0), (2, 0), (2, 2))
    name = 'Acacia Log'

class AcaciaWood(Block2):
    texture = tex_coords((2, 2), (2, 2), (2, 2))
    name = 'Acacia Wood'

class AcaciaPlanks(Block2):
    texture = tex_coords((2, 1), (2, 1), (2, 1))
    name = 'Acacia Planks'

class AcaciaLeaf(Block):
    texture = tex_coords((3, 0), (3, 0), (3, 0))
    name = 'Acacia Leaf'

class CraftTable(Block3):
    texture = tex_coords((1, 0), (3, 3), (0, 0))
    name = 'Crafting Table'

class Furnace(Block3):
    texture = tex_coords((2, 1), (2, 1), (2, 0), left = (1, 1), back=(1, 1))
    name = 'Furnace'

all_blocks = Block.__subclasses__() + Block2.__subclasses__() + Block3.__subclasses__()

CAVE_DIE = [Stone, BrownClay, SnowBlock, Dirt, GrassBlock, Sand, DiamondOre, GoldOre, RedstoneOre, IronOre, CoalOre, LapisOre]
