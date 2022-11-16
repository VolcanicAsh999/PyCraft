from pyglet.gl import *

__all__ = ["show_block", "hide_block", "show_sector", "hide_sector", "show_entity", "hide_entity"]

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.
    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
        ]

def rect_vertices(x, y, z, a, b, c):
    """ Return the vertices of the rectangle at position x, y, z with x-width a*2, z-depth b*2, and y-height c*2.
"""
    return [
        x-a,y+c,z-b, x-a,y+c,z+b, x+a,y+c,z+b, x+a,y+c,z-b,  # top
        x-a,y-c,z-b, x-a,y-c,z+b, x+a,y-c,z+b, x+a,y-c,z-b,  # bottom
        x-a,y-c,z-b, x-a,y-c,z+b, x-a,y+c,z+b, x-a,y+c,z-b,  # left
        x+a,y-c,z+b, x+a,y-c,z-b, x+a,y+c,z-b, x+a,y+c,z+b,  # right
        x-a,y-c,z+b, x+a,y-c,z+b, x+a,y+c,z+b, x-a,y+c,z+b,  # front
        x+a,y-c,z-b, x-a,y-c,z-b, x-a,y+c,z-b, x+a,y+c,z-b,  # back
        ]

class GraphicsEngine:
    def __init__(self):
        pass
    
    def show_block(self, model, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.
        """
        texture = model.world[position]
        model.shown[position] = texture
        if immediate:
            self._show_block(model, position, texture)
        return texture

    def _show_block(self, model, position, texture):
        """ Private implementation of the `show_block()` method.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture.texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        model._shown[position] = model.batch.add(24, GL_QUADS, texture.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, model, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.
        """
        if position in model.shown.keys():
            model.shown.pop(position)
        if immediate:
            self._hide_block(model, position)

    def _hide_block(self, model, position):
        """ Private implementation of the 'hide_block()` method.
        """
        if position in model._shown.keys():
            model._shown.pop(position).delete()

    def show_sector(self, model, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.
        """
        for position in model.sectors.get(sector, []):
            if position not in model.shown and model.exposed(position):
                model.show_block(position, False)

    def hide_sector(self, model, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.
        """
        for position in model.sectors.get(sector, []):
            if position in model.shown:
                model.hide_block(position, False)

    def show_rec(self, model, position, size, texture, group, immediate=True):
        model.shown[position] = texture
        if immediate:
            self._show_rec(model, position, size, texture, group)

    def _show_rec(self, model, position, size, texture, group):
        x, y, z = position
        x1, y1, z1 = size
        vertex_data = rect_vertices(x, y, z, x1/2, z1/2, y1/2)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        model._shown[position] = model.batch.add(24, GL_QUADS, group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_rec(self, model, position, immediate=True):
        if position in model.shown.keys():
            model.shown.pop(position)
        if immediate:
            self._hide_rec(model, position)

    def _hide_rec(self, model, position):
        if position in model._shown.keys():
            model._shown.pop(position).delete()

graphics_engine = GraphicsEngine()

show_block = graphics_engine.show_block
hide_block = graphics_engine.hide_block
show_sector = graphics_engine.show_sector
hide_sector = graphics_engine.hide_sector
show_rec = graphics_engine.show_rec
hide_rec = graphics_engine.hide_rec
