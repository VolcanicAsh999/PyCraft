from __future__ import division

import sys
import math
import random
import time
import itertools
import turtle
from tkinter import messagebox
from tkinter.simpledialog import askstring
turtle.textinput = askstring
import tkinter as tk
root=tk.Tk()
root.withdraw()
import os
import string

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

#import noise_gen1 as noise_gen
from noise_gen import NoiseGen
from blocks import *
import blocks
import graphics_engine as ge
import entities
from biomes import *


__version__ = '0.5.0'

TICKS_PER_SEC = 60

# Size of sectors used to ease block loading.
SECTOR_SIZE = 16

#Dimensions of the world in sectors
WORLD_SECTORS = 16

#Dimensions of the world in blocks
WORLD_BLOCKS = SECTOR_SIZE * WORLD_SECTORS

#Size of biomes (in sectors)
BIOME_SIZE = 4

#Dimensions of the world in biomes
WORLD_BIOMES = WORLD_SECTORS // BIOME_SIZE

WALKING_SPEED = 5
FLYING_SPEED = 15

#Whether or not the user is allowed to load/save the world
DO_WORLD_LOAD = False
DO_WORLD_SAVE = False

#Name of world
WORLD_NAME = 'test_world'

#World file
WORLD_PATH = os.path.join('pycraft_worlds', WORLD_NAME + '.txt')

GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.0 # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

PLAYER_HEIGHT = 2

USE_X = False
#USE_X = True

if sys.version_info[0] >= 3:
    xrange = range

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

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

#Whether or not to do cheats
CHEATS_ENABLED = True

#Gamemode
GAMEMODE = 'SURVIVAL'

#Seed of the world
if not DO_WORLD_LOAD:
    do_random = turtle.textinput('Random Seed', 'Do random seed?')
    if do_random.lower() == 'no' or do_random.lower() == 'n':
        SEED = turtle.textinput('Enter Seed', 'Enter the seed here')
        try:
            SEED = int(SEED)
        except ValueError:
            seed = ''
            for char in SEED:
                seed += str(ord(char))
            SEED = int(seed)
    else:
        seed = ''
        for char in xrange(random.randrange(3, 5)):
            seed += str(ord(random.choice(string.printable)))
        SEED = int(seed)
        
else:
    with open(WORLD_PATH) as file:
        exec('SEED = ' + file.readlines()[0].replace('\n', ''))

random.seed(SEED)

#Information of biomes

#Mapping of biomes to biome name
BIOMES = {}

#Information of world biome
BIOME_INFO = None

#The noise generator
GEN = NoiseGen(SEED, 'plains')
#noise_gen.start(SEED, b'plains')
#GEN = noise_gen

#Biome temperatures

def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.
    Parameters
    ----------
    position : tuple of len 3
    Returns
    -------
    block_position : tuple of ints of len 3
    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.
    Parameters
    ----------
    position : tuple of len 3
    Returns
    -------
    sector : tuple of len 3
    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)

def biomeize(position):
    """ Returns a tuple representing the biome for the given `position`.
    Parameters
    ----------
    position : tuple of len 3
    Returns
    -------
    biome : tuple of len 3
    """
    x, y, z = sectorize(position)
    x, y, z = x // BIOME_SIZE, y // BIOME_SIZE, z // BIOME_SIZE
    return (x, 0, z)

def biomeFromPos(position):
    """ Returns a string name representing the biome for the given `position`.
    Parameters
    ----------
    position : tuple of len 3
    Returns
    -------
    biome : a string of the biome name
    """
    x, y, z = biomeize(position)
    if (x, z) in BIOMES:
        return BIOMES[(x, z)]
    else:
        return 'out of world'

def get_info(biome):
    """Returns the info for the biome.
    Parameters
    ----------
    biome : string
    Returns
    -------
    biome : a dict of info for the biome
    """
    if biome == 'plains': biome = PLAINS
    if biome == 'forest': biome = FOREST
    if biome == 'mountains': biome = MOUNTAINS
    if biome == 'ocean': biome = OCEAN
    if biome == 'desert': biome = DESERT
    if biome == 'badlands': biome = BADLANDS
    if biome == 'deep_ocean': biome = DEEP_OCEAN
    if biome == 'wooded_hills': biome = WOODED_HILLS
    if biome == 'jungle': biome = JUNGLE
    if biome == 'tundra': biome = TUNDRA
    if biome == 'eroded_badlands': biome = ERODED_BADLANDS
    if biome == 'birch_forest': biome = BIRCH_FOREST
    if biome == 'dark_forest': biome = DARK_FOREST
    if biome == 'taiga': biome = TAIGA
    if biome == 'savanna': biome = SAVANNA
    if biome == 'swamp': biome = SWAMP
    return biome

def getSurroundingBiomes(pos):
    """ Returns a list of surrounding biomes.
    Parameters
    ----------
    pos : tuple of len 2
    Returns
    -------
    biomes : a list of surrounding biomes
    """
    biomes = []
    if pos[0] > 1:
        biomes.append(BIOMES[(pos[0] - 1, pos[1])])
    if pos[1] > 1:
        biomes.append(BIOMES[(pos[0], pos[1] - 1)])
    if pos[0] > 1 and pos[1] > 1:
        biomes.append(BIOMES[(pos[0] - 1, pos[1] - 1)])
    return biomes

def getAverageTemp(temp):
    """ Returns the average temperature of the surrounding biomes.
    Parameters
    ----------
    temp : list
    Returns
    -------
    temperature : the average temperature of the biomes
    """
    if len(temp) == 0:
        curr = GEN.get_biome().decode('utf-8') if USE_X else GEN.biome
        GEN.update_biome(b'mountains')
        temp = [GEN.getHeight(63, 97) / 50]
        GEN.update_biome(curr.encode('utf-8'))
    average = 0
    length = len(temp)
    for temperature in temp:
        average += temperature
    average /= length
    if 0.85 <= average <= 1.0:
        return 'hot'
    if 0.6 <= average < 0.85:
        return 'warm'
    if 0.35 <= average < 0.6:
        return 'neutral'
    if 0.0 <= average < 0.35:
        return 'cool'
    elif -1.0 <= average < 0.0:
        return 'cold'
    else:
        return 'cold'

def randIndex(x, z, lower, upper):
    if True:
        return random.randrange(lower, upper + 1)
    strseed = str(abs(SEED))
    n = int(strseed[0]) * x / (z + upper)
    n *= (lower + 1) * 2
    n /= (upper - 0.99999999999)
    print(n)
    return int(n)

def randTempUpdate(x, z):
    if True:
        return random.uniform(-0.2, 0.2)
    curr = GEN.biom if USE_X else GEN.biome
    GEN.update_biome(b'mountains')
    n = GEN.getHeight(x + 0.1 * 93.86, z - 0.2 * 37.092)
    GEN.update_biome(curr)
    n /= GEN.getHeight(0, 0) * 5.38
    n -= (GEN.getHeight(x * -37.93, z * 31.26) / 188.592)
    n += (GEN.getHeight(0, 0) / 264.492)
    if n < -0.2: n = -0.2
    if n > 0.2: n = 0.2
    return n

def doAddStructure(x, z, limit, underground=False):
    return random.randrange(0, limit) > limit - 2

HOUSES = []
CAVES = []
TOWERS = []
TREES = []
"""if DO_WORLD_LOAD:
    with open(WORLD_PATH) as file:
        info = file.readlines()
        exec('CAVES = ' + info[1].replace('\n', ''))
        exec('TREES = ' + info[2].replace('\n', ''))
        exec('HOUSES = ' + info[3].replace('\n', ''))
        exec('TOWERS = ' + info[4].replace('\n', ''))"""


class Model(object):

    def __init__(self, player):

        self.entitymanager = entities.EntityManager(self, player)

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        #Entities in world
        self.entities = []

        #Entities in world (shown)
        self.shown_entities = self.entities

        pyglet.clock.schedule_interval(self.entity_update, 1 / TICKS_PER_SEC)

        self.inter = 0

        self._initialize()

        self.entitymanager.update(1, self, player)

    def _initialize(self):
        """ Initialize the world by placing all the blocks.
        """

        global BIOME_INFO, GEN
        
        n = WORLD_BIOMES
        s = 1
        for x in xrange(0, n, s):
            for z in xrange(0, n, s):
                temp = []
                surrounding_biomes = getSurroundingBiomes((x, z))
                for biome in surrounding_biomes:
                    if biome in TEMP['hot']:
                        temp.append(1.0 + GEN.randTempUpdate(x, z))
                    elif biome in TEMP['cool']:
                        temp.append(0.2 + GEN.randTempUpdate(x, z))
                    elif biome in TEMP['warm']:
                        temp.append(0.7 + GEN.randTempUpdate(x, z))
                    elif biome in TEMP['neutral']:
                        temp.append(0.5 + GEN.randTempUpdate(x, z))
                    elif biome in TEMP['cold']:
                        temp.append(0.0 + GEN.randTempUpdate(x, z))
                averageTemp = getAverageTemp(temp)
                BIOMES[(x, z)] = TEMP[averageTemp][GEN.randIndex(x, z, 0, len(TEMP[averageTemp]) - 1)]

        print('Step one completed')
        print(BIOMES)
        n = WORLD_BLOCKS
        s = 1  # step size
        y = 0  # initial y height

        curr_biome = biomeFromPos((0, 0, 0))

        GEN.update_biome(curr_biome.encode('utf-8'))
        
        #too lazy to do this properly lol
        heightMap = []
        for x in xrange(0, n, s):
            for z in xrange(0, n, s):
                heightMap.append(0)
        for x in xrange(0, n, s):
            prevz = 0
            for z in xrange(0, n, s):
                if prevz - z <= BIOME_SIZE * SECTOR_SIZE:
                    curr_biome = biomeFromPos((x, 0, z))
                    GEN.update_biome(curr_biome.encode('utf-8'))
                    BIOME_INFO = get_info(curr_biome)
                    prevz = z
                heightMap[z + x * n] = int(GEN.getHeight(x, z))

        print('Step two completed')

        curr_biome = biomeFromPos((0, 0, 0))

        BIOME_INFO = get_info(curr_biome)

        #Generate the world
        for x in xrange(0, n, s):
            prevz = 0
            for z in xrange(0, n, s):
                h = heightMap[z + x * n]
                if prevz - z <= BIOME_SIZE * SECTOR_SIZE:
                    curr_biome = biomeFromPos((x, 0, z))
                    GEN.update_biome(curr_biome.encode('utf-8'))
                    BIOME_INFO = get_info(curr_biome)
                    prevz = z
                """if (h < BIOME_INFO['requiredWaterHeight'] - 2):
                    block = Sand
                    self.add_block((x, h - 1, z), block, immediate=False)
                    self.add_block((x, h - 2, z), block, immediate=False) 
                    for y in xrange (h, BIOME_INFO['requiredWaterHeight'] - 2):
                        self.add_block((x, y, z), Water, immediate=False)
                elif (h < BIOME_INFO['requiredWaterHeight'] - 1):
                    self.add_block((x, h, z), Sand, immediate=False)
                    self.add_block((x, h - 1, z), Sand, immediate=False)
                    self.add_block((x, h - 2, z), Sand, immediate=False)"""
                if True:#(h >= BIOME_INFO['requiredWaterHeight']):
                    self.add_block((x, h, z), BIOME_INFO['surfBlocks']['top'], immediate=False)
                    self.add_block((x, h - 1, z), BIOME_INFO['surfBlocks']['middle'], immediate=False)
                    self.add_block((x, h - 2, z), BIOME_INFO['surfBlocks']['bottom'], immediate=False)
                for y in xrange(h - 3, 0, -1):
                    self.add_block((x, y, z), Stone, immediate=False)

        print('Step three completed')

        curr_biome = biomeFromPos((0, 0, 0))

        BIOME_INFO = get_info(curr_biome)

        if True:#not DO_WORLD_LOAD:
            #Structure adding
            for x in xrange(0, n, s):
                prevz = 0
                for z in xrange(0, n, s):
                    h = heightMap[z + x * n]
                    if prevz - z <= BIOME_SIZE * SECTOR_SIZE:
                        curr_biome = biomeFromPos((x, 0, z))
                        GEN.update_biome(curr_biome.encode('utf-8'))
                        BIOME_INFO = get_info(curr_biome)
                        prevz = z
                    #Maybe add underground structure at this (x, z)
                    for h2 in xrange(h - 3, 0, -1):
                        if doAddStructure(x, z, BIOME_INFO['caveChance'], underground=True):
                            caveLen = GEN.randIndex(x, z, BIOME_INFO['caveSpecs']['len'][0], BIOME_INFO['caveSpecs']['len'][1])
                            caveWidth = GEN.randIndex(x, z, BIOME_INFO['caveSpecs']['width'][0], BIOME_INFO['caveSpecs']['width'][1])
                            dirs = []
                            new_dir = '+x'
                            for di in xrange(caveLen):
                                new_dir = ['+x', '+z', '-x', '-z', '+x+z', '-x-z', '+x-z', '-x+z', new_dir, new_dir, new_dir][random.randrange(0, 11)]#[GEN.randIndex(x, z, 0, 10)]
                                dirs.append(new_dir)
                            CAVES.append((x, h2, z, caveWidth // 2, dirs))
                    #Maybe add overground structure at this (x, z)
                    if (h > 20):
                        if 'tree' in BIOME_INFO['structures']:
                            if doAddStructure(x, z, BIOME_INFO['treeChance']):
                                treeType = BIOME_INFO['treeSpecs']['woodType'][GEN.randIndex(x, z, 0, len(BIOME_INFO['treeSpecs']['woodType']) - 1)]
                                giant = 1
                                if treeType in BIOME_INFO['treeSpecs']['canGrowGiant']:
                                    giant = GEN.randIndex(x, z, 0, BIOME_INFO['treeSpecs']['giantTreeChance'])
                                isBig = False
                                if giant != 0: #Normal tree
                                    treeHeight = GEN.randIndex(x, z, 5, 7)
                                else: #Giant tree
                                    treeHeight = GEN.randIndex(x, z, BIOME_INFO['treeSpecs']['giantHeight'][0], BIOME_INFO['treeSpecs']['giantHeight'][1])
                                    isBig = True
                                TREES.append((x, h, z, treeHeight, isBig, treeType))
                                continue
                        if 'house' in BIOME_INFO['structures']:
                            if doAddStructure(x, z, BIOME_INFO['houseChance']):
                                houseType = random.choice(['small_house_1', 'small_house_2', 'small_house_3', 'large_house_1'])#[GEN.randIndex(GEN.randIndex(x, z, 0, 3), GEN.randIndex(x, z, 0, 3), 0, 1)]
                                HOUSES.append((x, h, z, houseType))
                                continue
                        if 'tower' in BIOME_INFO['structures']:
                            if doAddStructure(x, z, BIOME_INFO['towerChance']):
                                towerHeight = GEN.randIndex(x, z, 18, 23)
                                TOWERS.append((x, h, z, towerHeight))
                                continue
                        
        print('Step four completed')
        print('Generating Trees... (', len(TREES), ')')
        for (x, h, z, treeHeight, isBig, treeType) in TREES:
            if treeType == 'oak':
                wood = OakLog
                leaf = OakLeaf
            if treeType == 'birch':
                wood = BirchLog
                leaf = BirchLeaf
            if treeType == 'dark oak':
                wood = DarkOakLog
                leaf = DarkOakLeaf
            if treeType == 'jungle':
                wood = JungleLog
                leaf = JungleLeaf
            if treeType == 'spruce':
                wood = SpruceLog
                leaf = SpruceLeaf
            if treeType == 'acacia':
                wood = AcaciaLog
                leaf = AcaciaLeaf
            if not isBig:
                #Tree trunk
                for y in xrange(h + 1, h + treeHeight):
                    self.add_block((x, y, z), wood, immediate=False)
                #Tree leaves
                leafh = h + treeHeight
                for lz in xrange(z + -2, z + 3):
                    for lx in xrange(x + -2, x + 3): 
                        for ly in xrange(3):
                            self.add_block((lx, leafh + ly, lz), leaf, immediate=False)
                for lz in xrange(z + -1, z + 2):
                    for lx in xrange(x + -1, x + 2):
                        self.add_block((lx, leafh + 3, lz), leaf, immediate=False)
            elif isBig:
                #Tree trunk
                for tx in xrange(x - 1, x + 1):
                    for tz in xrange(z - 1, z + 1):
                        for y in xrange(h + 1, h + treeHeight):
                            self.add_block((tx, y, tz), wood, immediate=False)
                #Tree leaves
                leafh = h + treeHeight
                for lz in xrange(z + -10, z + 11):
                    for lx in xrange(x + -10, x + 11):
                        for ly in xrange(3):
                            self.add_block((lx, leafh + ly, lz), leaf, immediate=False)
                for lz in xrange(z + -6, z + 7):
                    for lx in xrange(x + -6, x + 7):
                        for ly in xrange(2):
                            self.add_block((lx, leafh + ly + 3, lz), leaf, immediate=False)
                for lz in xrange(z + -1, z + 2):
                    for lx in xrange(x + -1, x + 2):
                        self.add_block((lx, leafh +5, lz), leaf, immediate=False)
        print('Generating Houses... (', len(HOUSES), ')')
        for (x, h, z, houseType) in HOUSES:
            if houseType == 'small_house_1':
                houseHeight = 7
                #Floor
                for wz in xrange(z + -4, z + 5):
                    for wx in xrange(x + -4, x + 5):
                        self.add_block((wx, h, wz), BRICK, immediate=False)
                #Walls
                for y in xrange(h + 1, h + houseHeight):
                    for wz in [z + -4, z + 4]:
                        for wx in xrange(x + -4, x + 4):
                            self.add_block((wx, y, wz), BRICK, immediate=False)
                    for wz in xrange(z + -4, z + 4):
                        for wx in [x + -4, x + 4]:
                            self.add_block((wx, y, wz), BRICK, immediate=False)
                    self.add_block((x + -4, y, z + -4), PLANKS, immediate=False)
                    self.add_block((x + 4, y, z + -4), PLANKS, immediate=False)
                    self.add_block((x + -4, y, z + 4), PLANKS, immediate=False)
                    self.add_block((x + 4, y, z + 4), PLANKS, immediate=False)
                #Roof
                for rx in xrange(x + -3, x + 4):
                    for rz in xrange(z + -3, z + 4):
                        self.add_block((rx, h + houseHeight, rz), BRICK, immediate=False)
                for rx in xrange(x + -2, x + 3):
                    for rz in xrange(z + -2, z + 3):
                        self.add_block((rx, h + houseHeight + 1, rz), BRICK, immediate=False)
                for rx in xrange(x + -1, x + 2):
                    for rz in xrange(z + -1, z + 2):
                        self.add_block((rx, h + houseHeight + 2, rz), BRICK, immediate=False)
                self.add_block((x, h + houseHeight + 3, z), PLANKS, immediate=False)
                #Hollow it out
                for y in xrange(h + 1, h + houseHeight):
                    for hz in xrange(z + -3, z + 4):
                        for hx in xrange(x + -3, x + 4):
                            self.remove_block((hx, y, hz), immediate=False)
                #Furnace
                self.add_block((x + 3, h + 1, z + -3), Furnace, immediate=False)
                #Door
                self.remove_block((x + -4, h + 1, z), immediate=False)
                self.remove_block((x + -4, h + 2, z), immediate=False)
                
            elif houseType == 'small_house_2':
                houseHeight = 8
                #Floor
                for wz in xrange(z + -4, z + 5):
                    for wx in xrange(x + -4, x + 5):
                        self.add_block((wx, h, wz), PLANKS, immediate=False)
                #Walls
                for y in xrange(h + 1, h + houseHeight):
                    for wz in [z + -4, z + 4]:
                        for wx in xrange(x + -4, x + 4):
                            self.add_block((wx, y, wz), PLANKS, immediate=False)
                    for wz in xrange(z + -4, z + 4):
                        for wx in [x + -4, x + 4]:
                            self.add_block((wx, y, wz), PLANKS, immediate=False)
                    self.add_block((x + -4, y, z + -4), LOG, immediate=False)
                    self.add_block((x + 4, y, z + -4), LOG, immediate=False)
                    self.add_block((x + -4, y, z + 4), LOG, immediate=False)
                    self.add_block((x + 4, y, z + 4), LOG, immediate=False)
                #Roof
                for rx in xrange(x + -3, x + 4):
                    for rz in xrange(z + -3, z + 4):
                        self.add_block((rx, h + houseHeight, rz), PLANKS, immediate=False)
                for rx in xrange(x + -2, x + 3):
                    for rz in xrange(z + -2, z + 3):
                        self.add_block((rx, h + houseHeight + 1, rz), PLANKS, immediate=False)
                for rx in xrange(x + -1, x + 2):
                    for rz in xrange(z + -1, z + 2):
                        self.add_block((rx, h + houseHeight + 2, rz), PLANKS, immediate=False)
                self.add_block((x, h + houseHeight + 3, z), LOG, immediate=False)
                #Hollow it out
                for y in xrange(h + 1, h + houseHeight):
                    for hz in xrange(z + -3, z + 4):
                        for hx in xrange(x + -3, x + 4):
                            self.remove_block((hx, y, hz), immediate=False)
                #Crafting Table, Furnace
                self.add_block((x + -3, h + 1, z + -3), CraftTable, immediate=False)
                self.add_block((x + -3, h + 1, z + -2), Furnace, immediate=False)
                #Door
                self.remove_block((x + -4, h + 1, z), immediate=False)
                self.remove_block((x + -4, h + 2, z), immediate=False)

            elif houseType == 'small_house_3':
                houseHeight = 6
                #Floor
                for wz in xrange(z + -4, z + 5):
                    for wx in xrange(x + -4, x + 5):
                        self.add_block((wx, h, wz), PLANKS, immediate=False)
                #Walls
                for y in xrange(h + 1, h + houseHeight):
                    for wz in [z + -4, z + 4]:
                        for wx in xrange(x + -4, x + 4):
                            self.add_block((wx, y, wz), STONE, immediate=False)
                    for wz in xrange(z + -4, z + 4):
                        for wx in [x + -4, x + 4]:
                            self.add_block((wx, y, wz), STONE, immediate=False)
                    self.add_block((x + -4, y, z + -4), LOG, immediate=False)
                    self.add_block((x + 4, y, z + -4), LOG, immediate=False)
                    self.add_block((x + -4, y, z + 4), LOG, immediate=False)
                    self.add_block((x + 4, y, z + 4), LOG, immediate=False)
                #Roof
                for rx in xrange(x + -3, x + 4):
                    for rz in xrange(z + -3, z + 4):
                        self.add_block((rx, h + houseHeight, rz), PLANKS, immediate=False)
                for rx in xrange(x + -2, x + 3):
                    for rz in xrange(z + -2, z + 3):
                        self.add_block((rx, h + houseHeight + 1, rz), PLANKS, immediate=False)
                for rx in xrange(x + -1, x + 2):
                    for rz in xrange(z + -1, z + 2):
                        self.add_block((rx, h + houseHeight + 2, rz), PLANKS, immediate=False)
                self.add_block((x, h + houseHeight + 3, z), PLANKS, immediate=False)
                #Hollow it out
                for y in xrange(h + 1, h + houseHeight):
                    for hz in xrange(z + -3, z + 4):
                        for hx in xrange(x + -3, x + 4):
                            self.remove_block((hx, y, hz), immediate=False)
                #Table
                self.add_block((x + -2, h + 1, z + -2), PLANKS, immediate=False)
                #Crafting Table
                self.add_block((x + 2, h + 1, z + 2), CraftTable, immediate=False)
                #Door
                self.remove_block((x + -4, h + 1, z), immediate=False)
                self.remove_block((x + -4, h + 2, z), immediate=False)

            elif houseType == 'large_house_1':
                houseHeight = 5
                #Hollow it out (must do first to do fast)
                for hz in xrange(z + -3, z + 4):
                    for hx in xrange(x + -9, x + 10):
                        for y in xrange(h + 1, h + houseHeight + houseHeight):
                            self.remove_block((hx, y, hz), immediate=False)
                #Lower Floor
                for wz in xrange(z + -4, z + 5):
                    for wx in xrange(x + -10, x + 11):
                        self.add_block((wx, h, wz), STONE, immediate=False)
                #Upper Floor
                for wz in xrange(z + -4, z + 5):
                    for wx in xrange(x + -10, x + 11):
                        self.add_block((wx, h + houseHeight, wz), STONE, immediate=False)
                #Lower Walls
                for y in xrange(h + 1, h + houseHeight):
                    for wz in [z + -4, z + 4]:
                        for wx in xrange(x + -10, x + 11):
                            self.add_block((wx, y, wz), PLANKS, immediate=False)
                    for wz in xrange(z + -4, z + 5):
                        for wx in [x + -10, x + 10]:
                            self.add_block((wx, y, wz), PLANKS, immediate=False)
                    self.add_block((x + -10, y, z + -4), LOG, immediate=False)
                    self.add_block((x + 10, y, z + -4), LOG, immediate=False)
                    self.add_block((x + -10, y, z + 4), LOG, immediate=False)
                    self.add_block((x + 10, y, z + 4), LOG, immediate=False)
                #Upper Walls
                for y in xrange(h + houseHeight + 1, h + houseHeight + houseHeight):
                    for wz in [z + -4, z + 4]:
                        for wx in xrange(x + -10, x + 11):
                            self.add_block((wx, y, wz), PLANKS, immediate=False)
                    for wz in xrange(z + -4, z + 5):
                        for wx in [x + -10, x + 10]:
                            self.add_block((wx, y, wz), PLANKS, immediate=False)
                    self.add_block((x + -10, y, z + -4), LOG, immediate=False)
                    self.add_block((x + 10, y, z + -4), LOG, immediate=False)
                    self.add_block((x + -10, y, z + 4), LOG, immediate=False)
                    self.add_block((x + 10, y, z + 4), LOG, immediate=False)
                #Steps
                self.add_block((x + 9, h + 1, z + 3), STONE, immediate=False)
                self.add_block((x + 8, h + 2, z + 3), STONE, immediate=False)
                self.add_block((x + 7, h + 3, z + 3), STONE, immediate=False)
                self.add_block((x + 6, h + 4, z + 3), STONE, immediate=False)
                self.add_block((x + 5, h + 5, z + 3), STONE, immediate=False)
                for sx in xrange(x + 6, x + 9):
                    self.remove_block((sx, h + 5, z + 3), immediate=False)
                #Roof
                for rx in xrange(x + -9, x + 10):
                    for rz in xrange(z + -3, z + 4):
                        self.add_block((rx, h + houseHeight + houseHeight, rz), PLANKS, immediate=False)
                for rx in xrange(x + -8, x + 9):
                    for rz in xrange(z + -2, z + 3):
                        self.add_block((rx, h + (houseHeight * 2) + 1, rz), PLANKS, immediate=False)
                for rx in xrange(x + -7, x + 8):
                    for rz in xrange(z + -1, z + 2):
                        self.add_block((rx, h + (houseHeight  * 2) + 2, rz), PLANKS, immediate=False)
                for rx in xrange(x + -6, x + 7):
                    self.add_block((rx, h + (houseHeight * 2) + 3, z), PLANKS, immediate=False)
                #Door
                self.remove_block((x, h + 1, z + -4), immediate=False)
                self.remove_block((x, h + 2, z + -4), immediate=False)
                #Tables
                self.add_block((x + -8, h + 1, z + -2), PLANKS, immediate=False)
                self.add_block((x + -8, h + houseHeight + 1, z + 2), PLANKS, immediate=False)
                #Garden Pool
                for wx in xrange(x + 5, x + 10):
                    for wz in xrange(z + -3, z + 2):
                        self.add_block((wx, h + 1, wz), GRASS, immediate=False)
                for wx in xrange(x + 6, x + 9):
                    for wz in xrange(z + -2, z + 1):
                        self.add_block((wx, h + 1, wz), WATER, immediate=False)
                #Crafting Table, Furnace
                self.add_block((x + -8, h + houseHeight + 1, z + -2), CraftTable, immediate=False)
                self.add_block((x + 8, h + houseHeight + 1, z + -3), Furnace, immediate=False)
                self.add_block((x + -8, h + 1, z + 3), CraftTable, immediate=False)
                self.add_block((x + -8, h + 1, z + 2), Furnace, immediate=False)
                #Windows
                for wx in [x + -4, x + -3, x + 3, x + 4]:
                    for wz in [z + -4, z + 4]:
                        self.remove_block((wx, h + houseHeight + 2, wz), immediate=False)
                
        print('Generating Towers... (', len(TOWERS), ')')
        for (x, h, z, towerHeight) in TOWERS:
            #Floor
            for wz in xrange(z + -2, z + 3):
                for wx in xrange(x + -2, x + 3):
                    self.add_block((wx, h, wz), STONE, immediate=False)
            #Walls
            for y in xrange(h + 1, h + towerHeight):
                for wz in [z + -2, z + 2]:
                    for wx in xrange(x + -2, x + 2):
                        self.add_block((wx, y, wz), STONE, immediate=False)
                for wz in xrange(z + -2, z + 2):
                    for wx in [x + -2, x + 2]:
                        self.add_block((wx, y, wz), STONE, immediate=False)
                self.remove_block((x + -2, y, z + -2), immediate=False)
                self.remove_block((x + 2, y, z + -2), immediate=False)
                self.remove_block((x + -2, y, z + 2), immediate=False)
                self.remove_block((x + 2, y, z + 2), immediate=False)
            #Overhang
            for oz in xrange(z + -4, z + 5):
                for ox in xrange(x + -4, x + 5):
                    self.add_block((ox, h + towerHeight, oz), STONE, immediate=False)
            self.remove_block((x + -4, h + towerHeight, z + -4), immediate=False)
            self.remove_block((x + 4, h + towerHeight, z + -4), immediate=False)
            self.remove_block((x + -4, h + towerHeight, z + 4), immediate=False)
            self.remove_block((x + 4, h + towerHeight, z + 4), immediate=False)
            #Terraces
            for tz in [z + -3, z + -1, z + 1, z + 3]:
                for tx in [x + -4, x + 4]:
                    self.add_block((tx, h + towerHeight + 1, tz), STONE, immediate=False)
            for tz in [z + -4, z + 4]:
                for tx in [x + -3, x + -1, x + 1, x + 3]:
                    self.add_block((tx, h + towerHeight + 1, tz), STONE, immediate=False)
            #Hollow it out
            for y in xrange(h + 1, h + towerHeight + 1):
                for hz in xrange(z + -1, z + 2):
                    for hx in xrange(x + -1, x + 2):
                        self.remove_block((hx, y, hz), immediate=False)
            #Door
            self.remove_block((x + -2, h + 1, z), immediate=False)
            self.remove_block((x + -2, h + 2, z), immediate=False)
        print('Generating Caves... (', len(CAVES), ')')
        for (x, h, z, caveWidth, dirs) in CAVES:
            #Entrance
            for ez in xrange(z + -(caveWidth // 2), z + (caveWidth // 2)):
                for ex in xrange(x + -(caveWidth // 2), x + (caveWidth // 2)):
                    for y in xrange(h, h + (caveWidth // 2) + 1):
                        if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
            for ez in xrange(z + -(caveWidth // 2) + 1, z + (caveWidth // 2) - 1):
                for ex in xrange(x + -(caveWidth // 2) + 1, x + (caveWidth // 2) - 1):
                    for y in [h, h + (caveWidth // 2)]:
                        if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
            for ez in [z + -(caveWidth // 2) + 1, z + (caveWidth // 2) - 1]:
                for ex in xrange(x + -(caveWidth // 2) + 1, x + (caveWidth // 2) - 1):
                    for y in xrange(h, h + (caveWidth // 2)):
                        if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
            for ez in xrange(z + -(caveWidth // 2) + 1, z + (caveWidth // 2) - 1):
                for ex in [x + -(caveWidth // 2) + 1, x + (caveWidth // 2) - 1]:
                    for y in xrange(h, h + (caveWidth // 2)):
                        if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
            #Lengthen it
            for new_dir in dirs:
                if True:
                    if new_dir == '+x+z':
                        (x, h, z) = (x + 1, h - 1, z + 1)
                    if new_dir == '-x-z':
                        (x, h, z) = (x - 1, h - 1, z - 1)
                    if new_dir == '+x-z':
                        (x, h, z) = (x + 1, h - 1, z - 1)
                    if new_dir == '-x+z':
                        (x, h, z) = (x - 1, h - 1, z + 1)
                    if new_dir == '+x':
                        (x, h, z) = (x + 1, h - 1, z)
                    if new_dir == '-x':
                        (x, h, z) = (x - 1, h - 1, z)
                    if new_dir == '+z':
                        (x, h, z) = (x, h - 1, z + 1)
                    if new_dir == '-z':
                        (x, h, z) = (x, h - 1, z - 1)
                for ez in xrange(z + -(caveWidth // 2), z + (caveWidth // 2)):
                    for ex in xrange(x + -(caveWidth // 2), x + (caveWidth // 2)):
                        for y in xrange(h, h + (caveWidth // 2) + 1):
                            if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
                for ez in xrange(z + -(caveWidth // 2) + 1, z + (caveWidth // 2) - 1):
                    for ex in xrange(x + -(caveWidth // 2) + 1, x + (caveWidth // 2) - 1):
                        for y in [h, h + (caveWidth // 2)]:
                            if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
                for ez in [z + -(caveWidth // 2) + 1, z + (caveWidth // 2) - 1]:
                    for ex in xrange(x + -(caveWidth // 2) + 1, x + (caveWidth // 2) - 1):
                        for y in xrange(h, h + (caveWidth // 2)):
                            if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
                for ez in xrange(z + -(caveWidth // 2) + 1, z + (caveWidth // 2) - 1):
                    for ex in [x + -(caveWidth // 2) + 1, x + (caveWidth // 2) - 1]:
                        for y in xrange(h, h + (caveWidth // 2)):
                            if (ex, y, ez) in self.world and self.world[(ex, y, ez)] in CAVE_DIE: self.remove_block((ex, y, ez), immediate=False)
        print('step five completed')
        #Bottom layer of the world
        for x in xrange(0, n, s):
            for z in xrange(0, n, s):
                self.add_block((x, 0, z), STONE, immediate=False)
        print('final step completed')

    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.
        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.
        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.
        """
        if position not in self.world:
            return
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        texture = ge.show_block(self, position, immediate)
        if not immediate:
            self._enqueue(ge.show_block, self, position, True)

    def hide_block(self, position, immediate=True):
        ge.hide_block(self, position, immediate)
        if not immediate:
            self._enqueue(ge.hide_block, self, position, True)

    def show_sector(self, sector):
        ge.show_sector(self, sector)
        for entity in self.entities:
            if entity.get_pos() in sector and entity not in self.shown_entities:
                self.shown_entities.append(entity)

    def hide_sector(self, sector):
        ge.hide_sector(self, sector)
        for entity in self.entities:
            if entity.get_pos() in sector and entity in self.shown_entities:
                self.shown_entities.append(entity)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.
        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.
        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.
        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False
        """
        start = time.time()
        while self.queue and time.time() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.
        """
        while self.queue:
            self._dequeue()

    def entity_update(self, dt):
        for entity in self.shown_entities:
            entity.update(self)


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # When flying gravity has no effect and speed is increased.
        self.flying = False if GAMEMODE != 'SPECTATOR' else True

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        biome = biomeize((30, 50, 80))
        GEN.update_biome(biomeFromPos(biome).encode('utf-8'))
        self.position = (30, int(GEN.getHeight(30, 80)) + 2, 80)
        #if DO_WORLD_LOAD:
        #    with open(WORLD_PATH, mode = 'r') as file:
        #        exec("self.position = " + file.readlines()[-2].replace('\n', ''))

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # Velocity in the y (upward) direction.
        self.dy = 0

        self.inventory = all_blocks

        self.index = 0

        # The current block the user can place. Hit num keys to cycle.
        self.block = self.inventory[self.index]

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model(self)

        # The labels that are displayed in the top left of the canvas.
        self.label_1 = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        self.label_2 = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 30, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))
        self.label_3 = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 50, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

        #The blocks in the actual inventory
        self.inv = []
        if DO_WORLD_LOAD:
            with open(WORLD_PATH, mode = 'r') as file:
                info = file.readlines()
                exec('self.inv = ' + info[5].replace('\n', ''))
                exec('self.position = ' + info[8].replace('\n', ''))
                #exec('self.block = ' + info[6].replace('\n', ''))
                exec('self.name = ' + info[7].replace('\n', ''))
                exec('self.index = ' + info[9].replace('\n', ''))
                n = info[6].replace('\n', '')
                for i in dir(blocks):
                    if i.lower() == n.lower():
                        self.block = getattr(blocks, i)
                        break

        self.in_water = False

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.
        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.
        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.
        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.
        Parameters
        ----------
        dt : float
            The change in time since the last call.
        """
        self.model.process_queue()
        sector = sectorize(self.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.
        Parameters
        ----------
        dt : float
            The change in time since the last call.
        """
        # walking
        speed = FLYING_SPEED if self.flying else WALKING_SPEED
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)
        if (int(x), int(y), int(z)) in self.model.world:
            if self.model.world[(int(x), int(y), int(z))] == WATER and self.in_water == False:
                self.in_water = True
                self.switch_fog_color(True)
            elif self.model.world[(int(x), int(y), int(z))] != WATER and self.in_water == True:
                self.in_water = False
                self.switch_fog_color(False)

    def switch_fog_color(self, inWater):
        if inWater:
            glClearColor(0.2, 0.19, 1.0, 1)
            glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.2, 0.19, 1.0, 1))
        else:
            glClearColor(0.5, 0.69, 1.0, 1)
            glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.
        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.
        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25 if GAMEMODE != 'SPECTATOR' else 0.5
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.model.world:
                        continue
                    elif self.model.world[tuple(op)] == WATER:
                        break
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break
        return tuple(p)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.
        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.
        """
        if self.exclusive:
            vector = self.get_sight_vector()
            block, previous = self.model.hit_test(self.position, vector)
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if previous and (self.block in self.inv or GAMEMODE == 'CREATIVE') and GAMEMODE != 'SPECTATOR':
                    self.model.add_block(previous, self.block)
                    if GAMEMODE != 'CREATIVE':
                        self.inv.remove(self.block)
            elif button == pyglet.window.mouse.LEFT and block and block[1] > 0:
                texture = self.model.world[block]
                if GAMEMODE != 'ADVENTURE' and GAMEMODE != 'SPECTATOR':
                    self.model.remove_block(block)
                    if GAMEMODE == 'SURVIVAL':
                        self.inv.append(texture)
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.
        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.
        """
        if self.exclusive:
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def nextblock(self, i=0):
        i += 1
        if i > len(self.inventory):
            self.index = 0
            self.block = self.inventory[self.index]
            return
        self.index += 1
        if self.index >= len(self.inventory):
            self.index = 0
        self.block = self.inventory[self.index]
        if self.block not in self.inv:
            self.nextblock(i)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.
        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.
        """
        global GAMEMODE
        if symbol == key.W:
            self.strafe[0] -= 1
        elif symbol == key.S:
            self.strafe[0] += 1
        elif symbol == key.A:
            self.strafe[1] -= 1
        elif symbol == key.D:
            self.strafe[1] += 1
        elif symbol == key.SPACE:
            if self.dy == 0:
                self.dy = JUMP_SPEED
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.TAB and GAMEMODE == 'CREATIVE':
            self.flying = not self.flying
        elif symbol == key._1:
            self.nextblock()
        elif symbol == key.T and CHEATS_ENABLED:
            self.set_exclusive_mouse(False)
            cheat_code = turtle.textinput('', '')
            if cheat_code.startswith('/gamemode '):
                cheat = cheat_code[10:]
                if cheat == 's' or cheat == '0' or cheat == 'survival':
                    GAMEMODE = 'SURVIVAL'
                    messagebox.showinfo('', 'The gamemode has been set to Survival')
                    self.flying = False
                if cheat == 'c' or cheat == '1' or cheat == 'creative':
                    GAMEMODE = 'CREATIVE'
                    messagebox.showinfo('', 'The gamemode has been set to Creative')
                if cheat == 'a' or cheat == '2' or cheat == 'adventure':
                    GAMEMODE = 'ADVENTURE'
                    messagebox.showinfo('', 'The gamemode has been set to Adventure')
                    self.flying = False
                if cheat == 'sp' or cheat == '3' or cheat == 'spectator':
                    GAMEMODE = 'SPECTATOR'
                    messagebox.showinfo('', 'The gamemode has been set to Spectator')
                    self.flying = True
            elif cheat_code.startswith('/tp '):
                cheat = cheat_code[4:]
                cheat_split = cheat.split(' ')
                p_pos = self.position
                try:
                    self.position = (int(cheat_split[0]), self.position[1], self.position[2])
                except Exception:
                    messagebox.showinfo('Error', f'argument {cheat_split[0]} must be a number')
                    self.position = p_pos
                    return
                try:
                    self.position = (self.position[0], int(cheat_split[1]), self.position[2])
                except Exception:
                    messagebox.showinfo('Error', f'argument {cheat_split[1]} must be a number')
                    self.position = p_pos
                    return
                try:
                    self.position = (self.position[0], self.position[1], int(cheat_split[2]))
                except Exception:
                    messagebox.showinfo('Error', f'argument {cheat_split[2]} must be a number')
                    self.position = p_pos
                    return
                messagebox.showinfo('', f'Teleported you to {self.position[0]}, {self.position[1]}, {self.position[2]}')
                
        elif symbol == key.V:
            if DO_WORLD_SAVE:
                with open(WORLD_PATH, mode='w') as file:
                    file.writelines([str(SEED) + '\n', str(CAVES) + '\n', str(TREES) + '\n', str(HOUSES) + '\n', str(TOWERS) + '\n', str(self.inv) + '\n', str(self.block.name) + '\n', self.block.name + '\n', str(self.position) + '\n', str(self.index) + '\n'])
                print('World Saved in ' + WORLD_PATH)

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.
        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.
        """
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1

    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.
        """
        # label
        self.label_1.y = height - 10
        self.label_2.y = height - 30
        self.label_3.y = height - 50
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.
        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.
        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.
        """
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self):
        """ Draw the label in the top left of the screen.
        """
        x, y, z = self.position
        amount = 0
        for block in self.inv:
            if block == self.block:
                amount += 1
                continue
        params = GEN.noiseParams
        self.label_1.text = 'FPS: %02d X:%.2f Y:%.2f Z:%.2f S:%d / W:%d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model._shown), len(self.model.world))
        self.label_2.text = 'SEED: %d Biome:%s BPos:%s' % (
            SEED, biomeFromPos(self.position).upper(), biomeize(self.position))
        self.label_3.text = 'Block: %s Amount: %d Gamemode:%s' % (
            self.block.name, amount, GAMEMODE)
        self.label_1.draw()
        self.label_2.draw()
        self.label_3.draw()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.
        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)


def setup_fog():
    """ Configure the OpenGL fog properties.
    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 40.0)
    glFogf(GL_FOG_END, 60.0)


def setup():
    """ Basic OpenGL configuration.
    """
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


def main():
    window = Window(width=1280, height=720, caption='Pycraft ' + __version__, resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()

if __name__ == '__main__':
    main()
