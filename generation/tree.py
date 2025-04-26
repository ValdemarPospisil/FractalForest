"""
Třídy pro generování 3D modelů stromů
"""
import random
import math
import numpy as np
import pyrr
from generation.l_system import LSystem
import logging

logger = logging.getLogger('FractalForest.Tree')

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
        logger.debug(f"Generating {self.tree_type} tree with {iterations} iterations")
        
        # Vygenerujeme řetězec představující strom
        l_string = self.l_system.generate(iterations)
        logger.debug(f"L-string generated, length: {len(l_string)}")
        
        # Převedeme řetězec na 3D model
        self.geometry = self._interpret_l_string(l_string)
        
        if self.geometry:
            vertices, normals, indices = self.geometry
            logger.debug(f"Tree geometry created: {len(vertices)} vertices, {len(indices)} indices")
        else:
            logger.error("Failed to generate tree geometry")        
    
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
        
        # Seznamy pro ukládání geometrie
        vertices = []
        normals = []
        indices = []
        
        # Základní tloušťka kmene
        thickness = 0.1 * self.scale
        
        # Předchozí pozice pro vytvoření válcových segmentů
        prev_position = position.copy()
        
        # Procházení L-řetězce
        segment_length = 0.5 * self.scale  # Délka jednoho segmentu
        current_index = 0  # Aktuální index vrcholu
        
        for char in l_string:
            if char == 'F':  # Kreslit segment
                # Výpočet nové pozice
                new_position = position + heading * segment_length
                
                # Vytvoření válcového segmentu (zjednodušeno jako kvádr)
                # Pro skutečný válec by bylo potřeba vytvořit kruh bodů v rovině kolmé na heading
                
                # Kolmý vektor na heading
                up = np.array([0.0, 1.0, 0.0])
                if np.allclose(heading, up) or np.allclose(heading, -up):
                    right = np.array([1.0, 0.0, 0.0])
                else:
                    right = np.cross(heading, up)
                    right = right / np.linalg.norm(right)
                
                up = np.cross(right, heading)
                up = up / np.linalg.norm(up)
                
                # Vytvoření čtyř bodů pro začátek segmentu
                p1 = prev_position + right * thickness + up * thickness
                p2 = prev_position + right * thickness - up * thickness
                p3 = prev_position - right * thickness - up * thickness
                p4 = prev_position - right * thickness + up * thickness
                
                # Vytvoření čtyř bodů pro konec segmentu
                # Tloušťka se zmenšuje s délkou řetězce
                segment_thickness = thickness * 0.8
                p5 = new_position + right * segment_thickness + up * segment_thickness
                p6 = new_position + right * segment_thickness - up * segment_thickness
                p7 = new_position - right * segment_thickness - up * segment_thickness
                p8 = new_position - right * segment_thickness + up * segment_thickness
                
                # Přidání všech vrcholů
                vertices.extend([p1, p2, p3, p4, p5, p6, p7, p8])
                
                # Výpočet normál (zjednodušeno)
                n1 = np.array([1.0, 0.0, 0.0])
                n2 = np.array([0.0, 0.0, -1.0])
                n3 = np.array([-1.0, 0.0, 0.0])
                n4 = np.array([0.0, 0.0, 1.0])
                n5 = np.array([1.0, 0.0, 0.0])
                n6 = np.array([0.0, 0.0, -1.0])
                n7 = np.array([-1.0, 0.0, 0.0])
                n8 = np.array([0.0, 0.0, 1.0])
                
                normals.extend([n1, n2, n3, n4, n5, n6, n7, n8])
                
                # Indexy pro vykreslení kvádru (6 stěn, každá má 2 trojúhelníky)
                # Přední stěna
                indices.extend([current_index, current_index + 1, current_index + 5])
                indices.extend([current_index, current_index + 5, current_index + 4])
                
                # Pravá stěna
                indices.extend([current_index + 1, current_index + 2, current_index + 6])
                indices.extend([current_index + 1, current_index + 6, current_index + 5])
                
                # Zadní stěna
                indices.extend([current_index + 2, current_index + 3, current_index + 7])
                indices.extend([current_index + 2, current_index + 7, current_index + 6])
                
                # Levá stěna
                indices.extend([current_index + 3, current_index + 0, current_index + 4])
                indices.extend([current_index + 3, current_index + 4, current_index + 7])
                
                # Horní stěna
                indices.extend([current_index + 4, current_index + 5, current_index + 6])
                indices.extend([current_index + 4, current_index + 6, current_index + 7])
                
                # Spodní stěna
                indices.extend([current_index + 0, current_index + 3, current_index + 2])
                indices.extend([current_index + 0, current_index + 2, current_index + 1])
                
                # Aktualizace indexu
                current_index += 8
                
                # Aktualizace pozice
                prev_position = new_position.copy()
                position = new_position.copy()
                
                # Zmenšení tloušťky pro další segment
                thickness = thickness * 0.95
                
            elif char == '+':  # Otočit doleva
                rotation = pyrr.matrix33.create_from_axis_rotation(
                    axis=left, 
                    theta=math.radians(self.l_system.angle)
                )
                heading = rotation @ heading
                heading = heading / np.linalg.norm(heading)
                
            elif char == '-':  # Otočit doprava
                rotation = pyrr.matrix33.create_from_axis_rotation(
                    axis=left, 
                    theta=-math.radians(self.l_system.angle)
                )
                heading = rotation @ heading
                heading = heading / np.linalg.norm(heading)
                
            elif char == '[':  # Uložit stav
                stack.append((position.copy(), heading.copy(), left.copy(), thickness))
                
            elif char == ']':  # Obnovit stav
                if stack:
                    position, heading, left, thickness = stack.pop()
                    prev_position = position.copy()
        
        # Převod seznamů na numpy pole
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        
        return (vertices, normals, indices)
        
    def get_model_matrix(self):
        """Vrací transformační matici pro strom"""
        # Vytvoření matic transformací
        translation = pyrr.matrix44.create_from_translation(self.position)
        
        # Rotace kolem y-osy pro náhodnou orientaci stromu
        rotation = pyrr.matrix44.create_from_y_rotation(random.uniform(0, 2 * math.pi))
        
        # Matice pro změnu měřítka
        scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([self.scale, self.scale, self.scale]))
        
        # Kombinace všech transformací
        model_matrix = pyrr.matrix44.multiply(rotation, scale)
        model_matrix = pyrr.matrix44.multiply(model_matrix, translation)
        
        return model_matrix
