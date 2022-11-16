import pyglet
import random
import blocks
import graphics_engine as ge
from pyglet.graphics import TextureGroup
from pyglet import image

group1 = TextureGroup(image.load('textures\\mobs\\mobs1.png').get_texture())

def tex_coord(x, y, n=4):
    """ Return the bounding vertices of the texture square.
    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

def get(x, y, nx, ny):
    return x, y, x + nx, y, x + nx, y + ny, x, y + ny

def tex_coor(ti, bi, fi, li, ri, bai):
    t=[]
    t.extend(get(ti[0], ti[1], ti[2], ti[3]))
    t.extend(get(bi[0], bi[1], bi[2], bi[3]))
    t.extend(get(fi[0], fi[1], fi[2], fi[3]))
    t.extend(get(li[0], li[1], li[2], li[3]))
    t.extend(get(ri[0], ri[1], ri[2], ri[3]))
    t.extend(get(bai[0], bai[1], bai[2], bai[3]))
    return t


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

def tex_coords_advanced(top, bottom, front, left=None, right=None, back=None, topsize=8, bottomsize=8, frontsize=8, leftsize=8, rightsize=8, backsize=8):
    """ Return a list of the texture squares for the top, bottom and side.
    """
    if not left:
        left = front
    if not right:
        right = left
    if not back:
        back = front
    top = tex_coord(*top,n=topsize)
    bottom = tex_coord(*bottom,n=bottomsize)
    front = tex_coord(*front,n=frontsize)
    left = tex_coord(*left,n=leftsize)
    right = tex_coord(*right,n=rightsize)
    back = tex_coord(*back,n=backsize)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(front)
    result.extend(left)
    result.extend(right)
    result.extend(back)
    return result


class BaseEntity:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.width = 0
        self.height = 0
        self.depth = 0
        self.texture = None
        self.texturegroup = None
        self.dx = self.dy = self.dz = 0
        self.move_speed = 70
        self.m = 70

    def get_size(self):
        return self.width, self.height, self.depth

    def get_pos(self):
        return self.x, self.y, self.z

    def get_texture(self):
        return self.texture

    def get_group(self):
        return self.texturegroup

    def get_data(self):
        return (self.get_texture(), self.get_group())

    def move(self, world):
        self.move_speed -= 1
        if self.move_speed <= 0:
            self.move_speed = self.m
            self.dx = random.choice([self.dx for i in range(10)] + [-1, 0, 1])
            self.dz = random.choice([self.dz for i in range(10)] + [-1, 0, 1])
            self.x += self.dx
            self.z += self.dz
        if (self.x, round(self.y), self.z) in world.keys():
            if world[(self.x, round(self.y), self.z)] != blocks.Water:
                self.dy = .1
            else:
                self.dy = 0
        else:
            if (self.x, round(self.y) - 1, self.z) in world.keys() and world[(self.x, round(self.y) - 1, self.z)] != blocks.Water:
                self.dy = 0
            else:
                self.dy = -.1
        self.y += self.dy

    def update(self, model):
        self.draw(model)

    def draw(self, model):
        pass


class Pig(BaseEntity):
    def __init__(self, x, y, z):
        super(Pig, self).__init__(x, y, z)
        self.texturehead = tex_coords_advanced((0, 0), (0, 0), (1, 0), back=(0, 0), left=(0, 0))
        self.texturebody = tex_coords_advanced((2, 0), (2, 0), (0, 0), back=(3.5, 0), left=(2, 0))
        self.texturefoot = tex_coords_advanced((0, 0), (0, 0), (0, 0))
        self.texturegroup = TextureGroup(image.load('textures\\mobs\\mobs1.png').get_texture())

    def draw(self, model):
        for x in [self.x + -.35, self.x + .35]:
            for z in [self.z + -.15, self.z + .35]:
                ge.hide_rec(model, (x, self.y - .1, z))
        ge.hide_rec(model, (self.x, self.y + 0.2, self.z + 0.4))
        ge.hide_rec(model, (self.x, self.y, self.z + 0.1))
        self.move(model.world)
        ge.show_rec(model, (self.x, self.y + 0.2, self.z + 0.4), (0.8, 0.8, 0.8), self.texturehead, self.texturegroup)
        ge.show_rec(model, (self.x, self.y, self.z + 0.1), (0.8, 0.6, 1.3), self.texturebody, self.texturegroup)
        for x in [self.x + -.35, self.x + .35]:
            for z in [self.z + -.15, self.z + .35]:
                ge.show_rec(model, (x, self.y - .1, z), (0.1, 0.2, 0.1), self.texturefoot, self.texturegroup)


class EntityManager:
    def __init__(self, model, player):
        pyglet.clock.schedule_interval(self.update, 20, model, player)

    def update(self, dt, model, player):
        model.entities.append(Pig(random.randint(int(player.position[0] + -32), int(player.position[0] + 32)), 80, random.randint(int(player.position[2] + -32), int(player.position[2] + 32))))
