"""
Třídy pro generování 3D modelů stromů
"""
import random
import math
import numpy as np
import pyrr
from generation.l_system import LSystem

class Tree:
    """Třída reprezentující 3D model stromu"""
    
    def __init__(self, position=(0, 0, 0), scale=1.0, tree_type="pine"):
        self.position = pyrr.Vector3(position)
        self.scale = scale
        self.tree_type = tree_type
        self.geometry = None  # (vertices, normals, indices)
        self.l_system = LSystem.create_tree_system(tree_type, randomness=0.1)
        self.color = self._get_color_for_type(tree_type)
        # Pro renderer
        self.vao = None
        
    def _get_color_for_type(self, tree_type):
        """Vrátí barvu pro daný typ stromu"""
        if tree_type == "pine":
            return (0.2, 0.5, 0.2)  # Tmavě zelená
        elif tree_type == "oak":
            return (0.3, 0.6, 0.3)  # Světlejší zelená
        elif tree_type == "bush":
            return (0.4, 0.7, 0.3)  # Žlutozelená
        else:
            return (0.3, 0.5, 0.2)  # Výchozí zelená
    
    def generate(self, iterations=3):
        """Generuje 3D model stromu pomocí L-systému"""
        # Vygenerujeme řetězec představující strom
        l_string = self.l_system.generate(iterations)
        
        # Převedeme řetězec na 3D model
        self.geometry = self._interpret_l_string(l_string)
        
    def _interpret_l_string(self, l_string):
        """
        Interpretuje řetězec L-systému jako 3D geometrii
        
        Parametry:
        - l_string: řetězec generovaný L-systémem
        
        Vrací:
        - tuple (vertices, normals, indices) reprezentující geometrii stromu
        """
        # Stavový stack pro ukládání pozic a orientací
        stack = []
        
        # Aktuální pozice a orientace
        position = np.array([0.0, 0.0, 0.0])
        heading = np.array([0.0, 1.0, 0.0])  # Směr růstu (počáteční je nahoru)
        left = np.array([-1.0, 0.0, 0.0])    # Vektor doleva od směru růstu
