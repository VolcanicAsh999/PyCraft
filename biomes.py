from blocks import *
import sys

DIRT = Dirt
GRASS = GrassBlock
LOG = OakLog
WOOD = OakWood
LEAF = OakLeaf
WATER = Water
SAND = Sand
STONE = Stone
BRICK = Brick
CLAY = BrownClay
SNOW = SnowBlock
PLANKS = OakPlanks

#biomes info

MOUNTAINS = {'structures': ['house',
                            'tower',
                            'tree'],
            'treeSpecs': {
                'woodType': ['oak',
                            'oak',
                            'birch'],
                'canGrowGiant': []
            },
            'surfBlocks': {
                'top': GRASS,
                'middle': DIRT,
                'bottom': STONE
            },
            'houseChance': 2000,
            'towerChance': 3000,
            'treeChance': 1000,
            'caveChance': 2000 + 50000,
            'requiredWaterHeight': 25,
            'caveSpecs': {
                'len': (14, 33),
                'width': (5, 10)
            }
}

PLAINS = {'structures': ['house',
                        'tower',
                        'tree'],
          'treeSpecs': {
              'woodType': ['oak',
                           'oak',
                          'oak',
                          'oak',
                          'birch'],
              'canGrowGiant': []
            },
            'surfBlocks': {
                    'top': GRASS,
                    'middle': DIRT,
                    'bottom': DIRT
            },
            'houseChance': 1000,
            'towerChance': 2000,
            'treeChance': 700,
            'caveChance': 7500 + 50000,
            'requiredWaterHeight': 25,
            'caveSpecs': {
                'len': (8, 17),
                'width': (3, 6)
            }
}

FOREST = {'structures': ['house',
                        'tower',
                        'tree'],
          'treeSpecs': {
              'woodType': ['oak',
                            'oak',
                            'oak',
                            'birch'],
             'canGrowGiant': []
            },
            'surfBlocks': {
                    'top': GRASS,
                    'middle': DIRT,
                    'bottom': DIRT
            },
            'houseChance': 1500,
            'towerChance': 3000,
            'treeChance': 155,
            'caveChance': 6000 + 50000,
            'requiredWaterHeight': 25,
            'caveSpecs': {
                'len': (8, 17),
                'width': (3, 6)
            }
}
OCEAN = {'structures': [],
        'surfBlocks': {
                'top': GRASS,
                'middle': DIRT,
                'bottom': DIRT
        },
        'caveChance': 10000 + 50000,
        'requiredWaterHeight': 25,
        'caveSpecs': {
            'len': (8, 17),
            'width': (3, 6)
        }
}
DEEP_OCEAN = {'structures': [],
            'surfBlocks': {
                    'top': GRASS,
                    'middle': DIRT,
                    'bottom': DIRT
            },
            'caveChance': 10000 + 50000,
            'requiredWaterHeight': 25,
            'caveSpecs': {
                'len': (8, 17),
                'width': (3, 6)
            }
}
WOODED_HILLS = {'structures': ['house',
                                'tower',
                                'tree'],
                'treeSpecs': {
                    'woodType': ['oak',
                                'oak',
                                'birch'],
                    'canGrowGiant': []
                },
                'surfBlocks': {
                        'top': GRASS,
                        'middle': DIRT,
                        'bottom': DIRT
                },
            'houseChance': 2000,
            'towerChance': 3000,
            'treeChance': 175,
            'caveChance': 2000 + 50000,
            'requiredWaterHeight': 25,
            'caveSpecs': {
                'len': (14, 33),
                'width': (5, 10)
            }
}
DESERT = {'structures': ['house'],
        'surfBlocks': {
                'top': SAND,
                'middle': SAND,
                'bottom': SAND
        },
        'houseChance': 2000,
        'caveChance': 6000 + 50000,
        'requiredWaterHeight': 25,
        'caveSpecs': {
            'len': (8, 17),
            'width': (3, 6)
        }
}
BADLANDS = {'structures': [],
            'surfBlocks': {
                    'top': CLAY,
                    'middle': CLAY,
                    'bottom': CLAY
            },
            'caveChance': 2000 + 50000,
            'requiredWaterHeight': 25,
            'caveSpecs': {
                'len': (14, 33),
                'width': (5, 10)
            }
}
JUNGLE = {'structures': ['house',
                        'tower',
                        'tree'],
        'treeSpecs': {
            'woodType': ['jungle',
                        'jungle',
                        'jungle',
                        'oak'],
            'giantTreeChance': 3,
            'canGrowGiant': ['jungle'],
            'giantHeight': (20, 30)
        },
        'surfBlocks': {
                'top': GRASS,
                'middle': DIRT,
                'bottom': DIRT
        },
        'houseChance': 3000,
        'towerChance': 2700,
        'treeChance': 115,
        'caveChance': 6000 + 50000,
        'requiredWaterHeight': 25,
        'caveSpecs': {
            'len': (8, 17),
            'width': (3, 6)
        }
}
ERODED_BADLANDS = {'structures': ['tower'],
                    'surfBlocks': {
                            'top': CLAY,
                            'middle': CLAY,
                            'bottom': CLAY
                    },
                    'towerChance': 3000,
                    'caveChance': 2000 + 50000,
                    'requiredWaterHeight': 50,
                    'caveSpecs': {
                        'len': (14, 33),
                        'width': (5, 14)
                    }
}
TUNDRA = {'structures': ['house',
                        'tower',
                        'tree'],
        'treeSpecs': {
            'woodType': ['spruce',
                        'spruce'],
            'canGrowGiant': []
        },
        'surfBlocks': {
                'top': SNOW,
                'middle': SNOW,
                'bottom': SNOW
        },
        'houseChance': 1000,
        'towerChance': 2000,
        'treeChance': 1000,
        'caveChance': 900 + 50000,
        'requiredWaterHeight': 25,
        'caveSpecs': {
            'len': (8, 17),
            'width': (3, 6)
        }
}
BIRCH_FOREST = {'structures': ['house',
                                'tower',
                                'tree'],
                'treeSpecs': {
                    'woodType': ['birch',
                                'birch'],
                    'giantTreeChance': 2,
                    'canGrowGiant': ['birch'],
                    'giantHeight': (10, 20)
                },
                'surfBlocks': {
                        'top': GRASS,
                        'middle': DIRT,
                        'bottom': DIRT
                },
                'houseChance': 1500,
                'towerChance': 3000,
                'treeChance': 155,
                'caveChance': 6000 + 50000,
                'requiredWaterHeight': 25,
                'caveSpecs': {
                    'len': (8, 17),
                    'width': (3, 6)
                }
}
DARK_FOREST = {'structures': ['house',
                            'tower',
                            'tree'],
                'treeSpecs': {
                    'woodType': ['dark oak',
                                'dark oak',
                                'dark oak',
                                'oak',
                                'birch'],
                    'giantTreeChance': 2,
                    'canGrowGiant': ['dark oak'],
                    'giantHeight': (3, 7)
                },
                'surfBlocks': {
                        'top': GRASS,
                        'middle': DIRT,
                        'bottom': DIRT
                },
                'houseChance': 1500,
                'towerChance': 3000,
                'treeChance': 115,
                'caveChance': 6000 + 50000,
                'requiredWaterHeight': 30,
                'caveSpecs': {
                    'len': (8, 17),
                    'width': (3, 6)
                }
}
TAIGA = {'structures': ['house',
                        'tower',
                        'tree'],
        'treeSpecs': {
            'woodType': ['spruce',
                        'spruce'],
            'canGrowGiant': []
        },
        'surfBlocks': {
                'top': GRASS,
                'middle': DIRT,
                'bottom': DIRT
        },
        'houseChance': 1500,
        'towerChance': 3000,
        'treeChance': 155,
        'caveChance': 6000 + 50000,
        'requiredWaterHeight': 25,
        'caveSpecs': {
            'len': (8, 17),
            'width': (3, 6)
        }
}
SAVANNA = {'structures': ['house',
                        'tower',
                        'tree'],
        'treeSpecs': {
            'woodType': ['acacia',
                        'acacia'],
            'canGrowGiant': []
        },
        'surfBlocks': {
                'top': GRASS,
                'middle': DIRT,
                'bottom': DIRT
        },
        'houseChance': 1000,
        'towerChance': 2000,
        'treeChance': 700,
        'caveChance': 7500 + 50000,
        'requiredWaterHeight': 25,
        'caveSpecs': {
            'len': (8, 17),
            'width': (3, 6)
        }
}
SWAMP = {'structures': ['house',
                        'tree'],
        'treeSpecs': {
            'woodType': ['oak'],
            'canGrowGiant': []
        },
        'surfBlocks': {
                'top': GRASS,
                'middle': DIRT,
                'bottom': DIRT
        },
        'houseChance': 2000,
        'towerChance': 2000,
        'treeChance': 900,
        'caveChance': 7500 + 50000,
        'requiredWaterHeight': 50,
        'caveSpecs': {
            'len': (8, 17),
            'width': (3, 6)
        }
}

TEMP = {
    'hot': [
            'desert',
            'savanna',
            'badlands',
            'badlands',
            'desert',
            'eroded_badlands',
            'desert'
    ],
    'warm': [
            'swamp',
            'swamp',
            'plains',
            'forest',
            'dark_forest',
            'birch_forest',
            'plains',
            'jungle',
            'dark_forest'
    ],
    'neutral': [
            'ocean',
            'ocean',
            'deep_ocean'
    ],
    'cool': [
            'taiga',
            'mountains',
            'wooded_hills',
            'mountains'
    ],
    'cold': [
            'tundra',
            'taiga'
    ]
}

for biome in [MOUNTAINS, PLAINS, FOREST, OCEAN, DEEP_OCEAN, WOODED_HILLS, DESERT, JUNGLE, BADLANDS, ERODED_BADLANDS, TUNDRA, BIRCH_FOREST, DARK_FOREST, TAIGA, SAVANNA, SWAMP]:
    biome['requiredWaterHeight'] = 60
