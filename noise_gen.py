import random as rand
import math

class NoiseParameters:
    def __init__(self, octaves, amplitude, smoothness, roughness, heightOffset):
        self.octaves = octaves #How fast the world gains height
        self.amplitude = amplitude #How sharp hills are
        self.smoothness = smoothness #How smooth the hills are
        self.roughness = roughness #How rough the hills are
        self.heightOffset = heightOffset #The height offset of the world

class NoiseGen:
    def __init__(self, seed, biome):
        self.seed = seed
        self.update_biome(biome)
        
    def update_biome(self, biome):
        heightOffset = 60
        if type(biome) == bytes: biome = biome.decode('utf-8')
        if biome == 'mountains' or biome == 'wooded_hills':
            octaves = 8
            amplitude = 70
            smoothness = 400
            roughness = 0.3
        if biome == 'plains' or biome == 'desert' or biome == 'tundra' or biome == 'savanna':
            octaves = 6
            amplitude = 40
            smoothness = 500
            roughness = 0.3
        if biome == 'forest' or biome == 'jungle' or biome == 'dark_forest' or biome == 'birch_forest' or biome == 'taiga' or biome == 'swamp':
            octaves = 7
            amplitude = 50
            smoothness = 450
            roughness = 0.3
        if biome == 'ocean':
            octaves = 7
            amplitude = 50
            smoothness = 450
            roughness = 0.3
            heightOffset = 0
        if biome == 'deep_ocean':
            octaves = 7
            amplitude = 50
            smoothness = 437
            roughness = 0.3
            heightOffset = -5
        if biome == 'badlands':
            octaves = 7
            amplitude = 90
            smoothness = 350
            roughness = 0.3
        if biome == 'eroded_badlands':
            octaves = 8
            amplitude = 80
            smoothness = 300
            roughness = 0.3
        else:
            octaves = 7
            amplitude = 35
            smoothness = 550
            roughness = 0.3
        self.biome = biome
        self.noiseParams = NoiseParameters(
            octaves, amplitude, smoothness, roughness, heightOffset
        )

    def _getNoise2(self, n):
        n += self.seed
        n = (int(n) << 13) ^ int(n)
        newn = (n * (n * n * 60493 + 19990303) + 1376312589) & 0x7fffffff
        return 1.0 - (float(newn) / 1073741824.0)

    def _getNoise(self, x, z):
        return self._getNoise2(x + z * 57)

    def _lerp(self, a, b, z):
        mu2 = (1.0 - math.cos(z * 3.14)) / 2.0
        return (a * (1 - mu2) + b * mu2)

    def _noise(self, x, z):
        floorX = float(int(x))
        floorZ = float(int(z))

        s = 0.0,
        t = 0.0,
        u = 0.0,
        v = 0.0;#Integer declaration

        s = self._getNoise(floorX,      floorZ)
        t = self._getNoise(floorX + 1,  floorZ)
        u = self._getNoise(floorX,      floorZ + 1)
        v = self._getNoise(floorX + 1,  floorZ + 1)

        rec1 = self._lerp(s, t, x - floorX)
        rec2 = self._lerp(u, v, x - floorX)
        rec3 = self._lerp(rec1, rec2, z - floorZ)
        return rec3

    def getHeight(self, x, z):
        totalValue = 0.0

        for a in range(self.noiseParams.octaves - 1):
            freq = math.pow(2.0, a)
            amp  = math.pow(self.noiseParams.roughness, a)
            totalValue += self._noise(
                (float(x)) * freq / self.noiseParams.smoothness,
                (float(z)) * freq / self.noiseParams.smoothness
            ) * self.noiseParams.amplitude

        result = (((totalValue / 2.1) + 1.2) * self.noiseParams.amplitude) + self.noiseParams.heightOffset

        final = (totalValue / 5) + self.noiseParams.heightOffset
        if final < 1: final = 1
        return final

    #def randIndex(self, x, z, lower, upper):
    #    o = self._lerp(upper, x, z) + self._getNoise(lower, z)
    #    s = self._getNoise(x, z)
    #    t = self._getNoise(z, x)
    #    u = self._getNoise2(upper)
    #    v = self._noise(s, x)
    #    w = self._lerp(t, o, v / 10)
    #    l = (w * self.seed) / (self._getNoise(t, u) * self.getHeight(lower, z))
    #    l /= self._noise(x * z, v * upper)
    #    l /= 124072573.27
    #    l = abs(l)
    #    if l == 0:
    #        l += abs(abs(self.randTempUpdate(98, 25) / upper) * self._getNoise(2, 1) + .5)
    #    l += lower
    #    if l < lower: l = lower
    #    if l > upper: l = upper
    #    return int(l)

    #def randTempUpdate(self, x, z):
    #    return self._getNoise(x, z) / 2.3
    def randTempUpdate(self, x, z):
        return rand.uniform(-0.2, 0.2)
    def randIndex(self, x, z, lower, upper):
        return rand.randint(lower, upper)

randIndex = NoiseGen(1010101010, 'mountains').randIndex
randTemp = NoiseGen(1010101010, 'mountains').randTempUpdate
