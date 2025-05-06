import random
import logging
import numpy as np
from typing import List, Tuple, Optional
from .tree import get_random_tree_type, get_tree_by_name, TreeDefinition, TREE_TYPES

class ForestGenerator:
    """Třída pro generování lesa s více stromy."""
    
    def __init__(self, 
                 renderer, 
                 area_size: float = 20.0, 
                 density: float = 0.5,
                 min_trees: int = 15,
                 max_trees: int = 25,
                 min_distance: float = 1.0):
        """
        Inicializuje generátor lesa.
        
        Args:
            renderer: Instance rendereru pro vykreslování stromů
            area_size: Velikost čtvercové oblasti pro generování lesa
            density: Hustota lesa (0.0 - 1.0), ovlivňuje počet stromů
            min_trees: Minimální počet stromů
            max_trees: Maximální počet stromů
            min_distance: Minimální vzdálenost mezi stromy
        """
        self.renderer = renderer
        self.area_size = area_size
        self.density = max(0.1, min(1.0, density))  # Omezení na 0.1-1.0
        self.min_trees = min_trees
        self.max_trees = max_trees
        self.min_distance = min_distance
        self.trees = []  # Seznam vygenerovaných stromů s pozicemi
        self.logger = logging.getLogger(__name__)
        
    def _calculate_tree_count(self) -> int:
        """Vypočítá počet stromů podle hustoty."""
        # Lineární interpolace mezi min a max podle hustoty
        count = int(self.min_trees + (self.max_trees - self.min_trees) * self.density)
        return count
    
    def _is_valid_position(self, pos: Tuple[float, float], positions: List[Tuple[float, float]]) -> bool:
        """Zkontroluje, zda je pozice dostatečně daleko od ostatních stromů."""
        for existing_pos in positions:
            # Výpočet vzdálenosti v rovině XZ
            dx = pos[0] - existing_pos[0]
            dz = pos[1] - existing_pos[1]
            distance = (dx**2 + dz**2)**0.5
            if distance < self.min_distance:
                return False
        return True
    
    def _generate_tree_positions(self, count: int) -> List[Tuple[float, float]]:
        """Generuje pozice stromů."""
        positions = []
        half_size = self.area_size / 2.0
        
        # Maximální počet pokusů pro umístění každého stromu
        max_attempts = 50
        
        for _ in range(count):
            positioned = False
            attempts = 0
            
            while not positioned and attempts < max_attempts:
                # Náhodná pozice v oblasti (x, z)
                x = random.uniform(-half_size, half_size)
                z = random.uniform(-half_size, half_size)
                
                # Zkontrolujeme, zda pozice vyhovuje minimální vzdálenosti
                if self._is_valid_position((x, z), positions):
                    positions.append((x, z))
                    positioned = True
                
                attempts += 1
            
            if not positioned:
                self.logger.warning(f"Couldn't position tree after {max_attempts} attempts")
        
        self.logger.info(f"Generated {len(positions)} valid tree positions")
        return positions
    
    def _select_tree_types(self, count: int) -> List[TreeDefinition]:
        """Vybere typy stromů pro les."""
        # Jednoduchá náhodná volba stromů
        tree_types = []
        for _ in range(count):
            tree_types.append(get_random_tree_type())
        
        return tree_types
    
    def generate_forest(self) -> List[Tuple[TreeDefinition, Tuple[float, float]]]:
        """
        Generuje les - vytváří stromy na různých pozicích.
        
        Returns:
            Seznam dvojic (definice_stromu, pozice_xz)
        """
        # Určení počtu stromů
        tree_count = self._calculate_tree_count()
        self.logger.info(f"Generating forest with {tree_count} trees (density: {self.density:.2f})")
        
        # Generování pozic pro stromy
        positions = self._generate_tree_positions(tree_count)
        
        # Vybrání typů stromů
        tree_types = self._select_tree_types(len(positions))
        
        # Vytvoření seznamu stromů s pozicemi
        self.trees = list(zip(tree_types, positions))
        
        return self.trees
    
    def render_forest(self):
        """Vykreslí vygenerovaný les."""
        if not self.trees:
            self.logger.warning("No trees to render, generate forest first")
            return
        
        # Odstranění všech stromů na scéně
        for i in range(len(self.trees)):
            self.renderer.setup_object(np.array([]), np.array([]), np.array([]), 
                                        object_id=f"tree_{i}")
        
        # Vykreslení všech stromů
        for i, (tree_def, position) in enumerate(self.trees):
            try:
                # Vygenerování stromu pomocí L-systému
                lsystem = tree_def.get_lsystem()
                iterations = tree_def.get_iterations()
                lsystem.generate(iterations)
                
                # Získání vrcholů, barev a normál
                vertices, colors, normals = lsystem.get_vertices()
                
                if vertices.size > 0:
                    # Posun vrcholů podle pozice stromu
                    x, z = position
                    transformed_vertices = vertices.copy()
                    
                    # Aplikování posunu pro každý třetí prvek (x, y, z)
                    for j in range(0, len(transformed_vertices), 3):
                        transformed_vertices[j] += x   # Posun X
                        transformed_vertices[j+2] += z  # Posun Z
                    
                    # Vykreslení stromu s unikátním ID
                    self.renderer.setup_object(transformed_vertices, colors, normals,
                                             object_id=f"tree_{i}")
                    
                    self.logger.debug(f"Rendered tree {i} ({tree_def.name}) at position ({x:.2f}, {z:.2f})")
                    
            except Exception as e:
                self.logger.exception(f"Error rendering tree {i}: {e}")
                
        self.logger.info(f"Rendered forest with {len(self.trees)} trees")
