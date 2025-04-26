"""
Modul pro generování lesa
"""
import random
import numpy as np
from generation.tree import Tree

class Forest:
    """Třída pro generování a správu lesa"""
    
    def __init__(self, size=50, density=0.5, tree_types=None, season="summer"):
        """
        Inicializace generátoru lesa
        
        Parametry:
        - size: velikost lesa (délka strany čtverce)
        - density: hustota stromů (0.0 - 1.0)
        - tree_types: seznam typů stromů, které se mají použít
        - season: roční období (ovlivňuje barvy)
        """
        self.size = size
        self.density = density
        self.tree_types = tree_types or ["pine", "oak", "bush"]
        self.season = season
        self.trees = []
        
    def generate(self):
        """Generuje stromy v lese podle zadaných parametrů"""
        # Vyčistíme existující les
        self.trees = []
        
        # Určíme počet stromů podle hustoty a velikosti lesa
        num_trees = int(self.size * self.size * self.density * 0.01)
        
        # Poloviční velikost oblasti pro lepší centrování
        half_size = self.size / 2
        
        # Generování stromů
        for _ in range(num_trees):
            # Náhodná pozice v rámci oblasti lesa
            x = random.uniform(-half_size, half_size)
            z = random.uniform(-half_size, half_size)
            
            # Náhodný typ stromu
            tree_type = random.choice(self.tree_types)
            
            # Náhodná velikost stromu s malými variacemi
            scale = random.uniform(0.8, 1.2)
            if tree_type == "bush":
                scale *= 0.6  # Keře jsou menší
            
            # Vytvoření stromu
            tree = Tree(position=(x, 0, z), scale=scale, tree_type=tree_type)
            
            # Generování geometrie stromu
            iterations = 3
            if tree_type == "pine":
                iterations = 4  # Jehličnany mají více iterací pro hustší větve
            elif tree_type == "bush":
                iterations = 2  # Keře mají méně iterací
                
            tree.generate(iterations=iterations)
            
            # Přidání stromu do lesa
            self.trees.append(tree)
            
    def update_season(self, season):
        """
        Aktualizuje roční období, což ovlivní barvy stromů
        
        Parametry:
        - season: nové roční období (summer, autumn, winter, spring)
        """
        self.season = season
        # Implementace změn barev podle ročního období by byla zde
        
    def get_tree_at(self, position, radius=1.0):
        """
        Najde strom na zadané pozici (nebo v jejím okolí)
        
        Parametry:
        - position: pozice v prostoru (x, z)
        - radius: poloměr hledání
        
        Vrací:
        - nejbližší strom nebo None
        """
        closest_tree = None
        min_distance = float('inf')
        
        for tree in self.trees:
            # Výpočet vzdálenosti v rovině XZ
            dx = tree.position[0] - position[0]
            dz = tree.position[2] - position[2]
            distance = (dx*dx + dz*dz) ** 0.5
            
            if distance < radius and distance < min_distance:
                closest_tree = tree
                min_distance = distance
                
        return closest_tree
