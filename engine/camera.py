import numpy as np
import math
import logging

# Nastavení loggeru
logger = logging.getLogger('FractalForest.Camera')

class Camera:
    def __init__(self, width, height):
        logger.info("Inicializace kamery")
        
        # Pozice kamery a orientace
        self.position = np.array([0.0, 5.0, 10.0], dtype=np.float32) 
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        # Nastavení projekce
        self.fov = 45.0
        self.aspect_ratio = width / height
        self.near = 0.1
        self.far = 100.0
        
        # Cache pro matice (aby nebyly počítány pokaždé znovu)
        self._view_matrix = None
        self._projection_matrix = None
        self._view_dirty = True
        self._projection_dirty = True
        
        logger.info(f"Kamera inicializována na pozici {self.position}")
    
    def set_projection(self, width, height):
        """Aktualizuje projekční matici při změně velikosti okna"""
        logger.info(f"Aktualizace projekce kamery pro okno {width}x{height}")
        self.aspect_ratio = width / height
        self._projection_dirty = True
    
    def get_view_matrix(self):
        """Vrátí view matici pro aktuální pozici kamery"""
        if self._view_dirty or self._view_matrix is None:
            # Výpočet pohledové matice
            z = self.position - self.target
            z = z / np.linalg.norm(z)
            
            x = np.cross(self.up, z)
            x = x / np.linalg.norm(x)
            
            y = np.cross(z, x)
            y = y / np.linalg.norm(y)
            
            translation = np.array([
                [1.0, 0.0, 0.0, -self.position[0]],
                [0.0, 1.0, 0.0, -self.position[1]],
                [0.0, 0.0, 1.0, -self.position[2]],
                [0.0, 0.0, 0.0, 1.0]
            ], dtype=np.float32)
            
            rotation = np.array([
                [x[0], x[1], x[2], 0.0],
                [y[0], y[1], y[2], 0.0],
                [z[0], z[1], z[2], 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ], dtype=np.float32)
            
            self._view_matrix = rotation @ translation
            self._view_dirty = False
            
        return self._view_matrix
    
    def get_projection_matrix(self):
        """Vrátí projekční matici pro nastavení kamery"""
        if self._projection_dirty or self._projection_matrix is None:
            # Výpočet perspektivní projekční matice
            f = 1.0 / math.tan(math.radians(self.fov) / 2.0)
            
            self._projection_matrix = np.array([
                [f / self.aspect_ratio, 0.0, 0.0, 0.0],
                [0.0, f, 0.0, 0.0],
                [0.0, 0.0, (self.far + self.near) / (self.near - self.far), (2 * self.far * self.near) / (self.near - self.far)],
                [0.0, 0.0, -1.0, 0.0]
            ], dtype=np.float32)
            
            self._projection_dirty = False
            
        return self._projection_matrix
    
    def move(self, dx, dy, dz):
        """Posun kamery"""
        self.position[0] += dx
        self.position[1] += dy
        self.position[2] += dz
        self._view_dirty = True
        logger.debug(f"Kamera posunuta na {self.position}")
