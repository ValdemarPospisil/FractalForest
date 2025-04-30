"""
Utility funkce pro rendering v Ursina engine
"""
from ursina import *
import numpy as np
import random
import logging

logger = logging.getLogger(__name__)

class TerrainGenerator:
    """
    Třída pro generování terénu v Ursina engine
    """
    def __init__(self, size=50.0, resolution=64):
        """
        Inicializace generátoru terénu
        
        Parametry:
        - size: velikost terénu
        - resolution: rozlišení meshe (počet vertexů na stranu)
        """
        self.size = size
        self.resolution = resolution
        self.mesh = None
        self.terrain_entity = None
        
    def generate_heightmap(self, seed=None, octaves=4, persistence=0.5, lacunarity=2.0, amplitude=1.5):
        """
        Generuje výškovou mapu pro terén
        
        Parametry:
        - seed: seed pro generování terénu
        - octaves: počet oktáv pro perlin noise
        - persistence: persistence šumu
        - lacunarity: "lacunarity" šumu
        - amplitude: amplituda výšky terénu
        
        Vrací:
        - numpy array s výškovými hodnotami
        """
        from noise import pnoise2
        
        if seed is None:
            seed = random.randint(0, 10000)
            logger.info(f"Vytvořen náhodný seed: {seed}")
        
        # Vytvoření prázdné výškové mapy
        heightmap = np.zeros((self.resolution, self.resolution))
        
        # Generování perlin noise
        scale = 10.0  # Měřítko šumu
        
        for i in range(self.resolution):
            for j in range(self.resolution):
                x = i / self.resolution * scale
                y = j / self.resolution * scale
                
                # Generování perlin noise s více oktávami
                noise_val = 0
                for octave in range(octaves):
                    freq = lacunarity ** octave
                    weight = persistence ** octave
                    noise_val += pnoise2(x * freq, y * freq, base=seed) * weight
                
                # Normalizace a škálování
                heightmap[i, j] = noise_val * amplitude
        
        return heightmap
    
    def create_terrain_mesh(self, heightmap=None):
        """
        Vytvoří mesh pro terén
        
        Parametry:
        - heightmap: výšková mapa pro terén (pokud None, vytvoří rovný terén)
        
        Vrací:
        - Ursina Mesh
        """
        # Velikost dlaždice
        tile_size = self.size / (self.resolution - 1)
        
        # Pozice vertexů
        vertices = []
        triangles = []
        uvs = []
        normals = []
        colors = []
        
        # Generování vertexů
        for z in range(self.resolution):
            for x in range(self.resolution):
                # Pozice
                pos_x = x * tile_size - self.size / 2
                pos_z = z * tile_size - self.size / 2
                
                # Výška
                height = 0
                if heightmap is not None:
                    height = heightmap[x, z]
                
                vertices.append((pos_x, height, pos_z))
                
                # UV mapování
                u = x / (self.resolution - 1)
                v = z / (self.resolution - 1)
                uvs.append((u, v))
                
                # Barva podle výšky
                if height < 0:
                    # Voda
                    colors.append((0.2, 0.3, 0.8, 1.0))
                elif height < 0.2:
                    # Písek
                    colors.append((0.8, 0.8, 0.6, 1.0))
                elif height < 0.5:
                    # Tráva
                    colors.append((0.3, 0.6, 0.3, 1.0))
                elif height < 1.0:
                    # Skála
                    colors.append((0.6, 0.6, 0.6, 1.0))
                else:
                    # Sníh
                    colors.append((0.9, 0.9, 0.9, 1.0))
        
        # Výpočet trojúhelníků
        for z in range(self.resolution - 1):
            for x in range(self.resolution - 1):
                # Indexy čtyř vrcholů tvořících čtverec
                i0 = z * self.resolution + x
                i1 = z * self.resolution + (x + 1)
                i2 = (z + 1) * self.resolution + x
                i3 = (z + 1) * self.resolution + (x + 1)
                
                # Dva trojúhelníky tvořící jeden čtverec
                triangles.append((i0, i2, i1))
                triangles.append((i1, i2, i3))
        
        # Výpočet normál pro každý vertex
        for i in range(len(vertices)):
            normals.append((0, 1, 0))  # Výchozí normála nahoru
        
        # Aktualizace normál na základě sousedních trojúhelníků
        for t in triangles:
            # Získání tří vertexů trojúhelníku
            v0 = np.array(vertices[t[0]])
            v1 = np.array(vertices[t[1]])
            v2 = np.array(vertices[t[2]])
            
            # Výpočet hran
            edge1 = v1 - v0
            edge2 = v2 - v0
            
            # Výpočet normály trojúhelníku
            normal = np.cross(edge1, edge2)
            normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else np.array([0, 1, 0])
            
            # Přidání této normály ke každému vertexu trojúhelníku
            normals[t[0]] = np.add(normals[t[0]], normal)
            normals[t[1]] = np.add(normals[t[1]], normal)
            normals[t[2]] = np.add(normals[t[2]], normal)
        
        # Normalizace normál
        for i in range(len(normals)):
            norm = np.linalg.norm(normals[i])
            if norm > 0:
                normals[i] = normals[i] / norm
        
        # Vytvoření meshe
        mesh = Mesh(
            vertices=vertices,
            triangles=triangles,
            uvs=uvs,
            normals=normals,
            colors=colors
        )
        
        self.mesh = mesh
        return mesh
    
    def create_terrain_entity(self, heightmap=None, texture=None):
        """
        Vytváří entitu terénu v Ursina
        
        Parametry:
        - heightmap: výšková mapa pro terén (pokud None, vytvoří rovný terén)
        - texture: textura pro terén
        
        Vrací:
        - Ursina Entity
        """
        # Vytvoření meshe
        if not self.mesh:
            self.create_terrain_mesh(heightmap)
        
        # Vytvoření entity
        self.terrain_entity = Entity(
            model=self.mesh,
            texture=texture,
            collider='mesh'
        )
        
        return self.terrain_entity

class SkyboxHandler:
    """
    Třída pro vytvoření a správu skyboxu v Ursina
    """
    def __init__(self, time_of_day='day'):
        """
        Inicializace handleru pro skybox
        
        Parametry:
        - time_of_day: denní doba ('day', 'sunset', 'night')
        """
        self.time_of_day = time_of_day
        self.skybox_entity = None
        self.initialize()
    
    def initialize(self):
        """
        Inicializuje skybox podle denní doby
        """
        if self.time_of_day == 'day':
            sky_color = color.rgb(135, 206, 235)  # Světle modrá
            horizon_color = color.rgb(200, 240, 255)  # Světle modrá s bílou
        elif self.time_of_day == 'sunset':
            sky_color = color.rgb(150, 100, 180)  # Fialová
            horizon_color = color.rgb(255, 180, 100)  # Oranžová
        elif self.time_of_day == 'night':
            sky_color = color.rgb(10, 10, 50)  # Tmavě modrá
            horizon_color = color.rgb(20, 20, 60)  # Trochu světlejší modrá
        else:
            # Výchozí
            sky_color = color.rgb(135, 206, 235)
            horizon_color = color.rgb(200, 240, 255)
        
        # Vytvoření skyboxu
        self.skybox_entity = Sky(color=sky_color, texture=None)
        
        # Pokud máme k dispozici texturu, můžeme použít:
        # self.skybox_entity = Sky(texture='path/to/skybox_texture')
        
        # Vytvoření slunce/měsíce
        if self.time_of_day == 'day':
            sun_position = (10, 10, 10)
            sun_color = color.rgb(255, 255, 200)  # Světle žlutá
            sun_intensity = 0.8
            
            # Vytvoření slunce
            self.sun = DirectionalLight(color=sun_color, intensity=sun_intensity)
            self.sun.look_at(Vec3(*sun_position))
            
            # Vytvoření vizuálního slunce
            self.sun_visual = Entity(
                model='sphere',
                color=sun_color,
                scale=5,
                position=Vec3(*sun_position) * 10,  # Daleko
                texture=None,
                glow=True
            )
        elif self.time_of_day == 'night':
            moon_position = (10, 5, 10)
            moon_color = color.rgb(200, 200, 255)  # Světle modrá
            moon_intensity = 0.3
            
            # Vytvoření měsíčního světla
            self.moon = DirectionalLight(color=moon_color, intensity=moon_intensity)
            self.moon.look_at(Vec3(*moon_position))
            
            # Vytvoření vizuálního měsíce
            self.moon_visual = Entity(
                model='sphere',
                color=moon_color,
                scale=3,
                position=Vec3(*moon_position) * 10,  # Daleko
                texture=None
            )
    
    def change_time_of_day(self, time_of_day):
        """
        Změna denní doby
        
        Parametry:
        - time_of_day: denní doba ('day', 'sunset', 'night')
        """
        # Uložení nové hodnoty
        self.time_of_day = time_of_day
        
        # Odstranění existujícího skyboxu
        if self.skybox_entity:
            destroy(self.skybox_entity)
            
        # Vytvoření nového skyboxu
        self.initialize()

class LightingSystem:
    """
    Třída pro správu světel ve scéně
    """
    def __init__(self):
        """
        Inicializace lighting systému
        """
        self.lights = []
        
    def add_directional_light(self, direction=(0, -1, 0), color=color.white, intensity=1.0):
        """
        Přidá směrové světlo
        
        Parametry:
        - direction: směr světla
        - color: barva světla
        - intensity: intenzita světla
        
        Vrací:
        - DirectionalLight
        """
        light = DirectionalLight(color=color * intensity)
        light.look_at(Vec3(*direction))
        self.lights.append(light)
        return light
    
    def add_point_light(self, position=(0, 0, 0), color=color.white, intensity=1.0, range=10):
        """
        Přidá bodové světlo
        
        Parametry:
        - position: pozice světla
        - color: barva světla
        - intensity: intenzita světla
        - range: dosah světla
        
        Vrací:
        - PointLight
        """
        light = PointLight(color=color * intensity, position=Vec3(*position), range=range)
        self.lights.append(light)
        return light
    
    def add_ambient_light(self, color=color.rgba(255, 255, 255, 128), intensity=0.3):
        """
        Přidá ambientní