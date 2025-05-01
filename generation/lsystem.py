import numpy as np
import random
import math
from typing import List, Tuple, Dict

class LSystem:
    def __init__(self, tree_definition):
        self.axiom = tree_definition.axiom
        self.rules = tree_definition.rules
        self.iterations = tree_definition.iterations
        self.angle = tree_definition.angle
        self.thickness_ratio = tree_definition.thickness_ratio
        self.length_ratio = tree_definition.length_ratio
        self.random_angle_variation = tree_definition.random_angle_variation
        self.random_length_variation = tree_definition.random_length_variation
        self.current_string = self.axiom
        self.color = tree_definition.color
        
        # Základní délka segmentu
        self.base_length = tree_definition.base_length
        # Základní tloušťka segmentu
        self.base_thickness = tree_definition.base_thickness
        
        # Výsledná geometrie
        self.vertices = []
        self.indices = []

    def generate(self):
        """Generuje řetězec L-systému na základě pravidel"""
        result = self.axiom
        
        for _ in range(self.iterations):
            next_result = ""
            for char in result:
                if char in self.rules:
                    # Přidáme náhodné variace do pravidel pro větší rozmanitost
                    if isinstance(self.rules[char], list):
                        # Pokud máme více možných pravidel pro symbol, vybereme náhodně jedno
                        replacement = random.choice(self.rules[char])
                    else:
                        replacement = self.rules[char]
                    next_result += replacement
                else:
                    next_result += char
            result = next_result
        
        self.current_string = result
        return result

    def create_geometry(self) -> Tuple[List[float], List[int]]:
        """Vytvoří 3D geometrii stromu na základě vygenerovaného řetězce L-systému"""
        # Reset geometrie
        self.vertices = []
        self.indices = []
        
        # Zásobník stavů pro větvení
        stack = []
        
        # Aktuální pozice, směr, délka a tloušťka
        position = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 1.0, 0.0])  # Začínáme růst nahoru (y+)
        length = self.base_length
        thickness = self.base_thickness
        
        # Pomocné vektory pro orientaci segmentů
        up = np.array([0.0, 1.0, 0.0])
        
        # Index pro vrcholy
        vertex_index = 0
        
        # Interpretace řetězce L-systému
        for char in self.current_string:
            if char == 'F':  # Posun a vytvoření segmentu
                # Náhodná variace délky
                current_length = length * (1.0 + random.uniform(-self.random_length_variation, self.random_length_variation))
                
                # Koncový bod segmentu
                new_position = position + direction * current_length
                
                # Vytvoření válce (zjednodušeně jako 8-boký hranol)
                self._create_cylinder_segment(position, new_position, thickness, self.color, vertex_index)
                vertex_index += 16  # 8 vrcholů nahoře + 8 vrcholů dole
                
                # Aktualizace pozice
                position = new_position
                
                # Zmenšení tloušťky a délky pro další segment
                thickness *= self.thickness_ratio
                length *= self.length_ratio
                
            elif char == '+':  # Rotace doprava kolem osy Z
                angle_rad = math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
                self._rotate_direction(direction, up, angle_rad)
                
            elif char == '-':  # Rotace doleva kolem osy Z
                angle_rad = -math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
                self._rotate_direction(direction, up, angle_rad)
                
            elif char == '&':  # Rotace dolů kolem osy X
                angle_rad = math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
                right = np.cross(direction, up)
                right = right / np.linalg.norm(right) if np.linalg.norm(right) > 0 else np.array([1.0, 0.0, 0.0])
                self._rotate_direction(direction, right, angle_rad)
                up = np.cross(right, direction)
                up = up / np.linalg.norm(up)
                
            elif char == '^':  # Rotace nahoru kolem osy X
                angle_rad = -math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
                right = np.cross(direction, up)
                right = right / np.linalg.norm(right) if np.linalg.norm(right) > 0 else np.array([1.0, 0.0, 0.0])
                self._rotate_direction(direction, right, angle_rad)
                up = np.cross(right, direction)
                up = up / np.linalg.norm(up)
                
            elif char == '\\':  # Rotace doprava kolem osy Y
                angle_rad = math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
                self._rotate_direction(up, direction, angle_rad)
                
            elif char == '/':  # Rotace doleva kolem osy Y
                angle_rad = -math.radians(self.angle + random.uniform(-self.random_angle_variation, self.random_angle_variation))
                self._rotate_direction(up, direction, angle_rad)
                
            elif char == '[':  # Uložení stavu na zásobník
                stack.append((position.copy(), direction.copy(), up.copy(), length, thickness))
                
            elif char == ']':  # Obnovení stavu ze zásobníku
                if stack:
                    position, direction, up, length, thickness = stack.pop()
        
        # Převedení seznamů na numpy pole pro ModernGL
        vertices_array = np.array(self.vertices, dtype=np.float32)
        indices_array = np.array(self.indices, dtype=np.uint32)
        
        return vertices_array, indices_array

    def _rotate_direction(self, vector, axis, angle):
        """Rotace vektoru kolem osy o daný úhel (v radiánech)"""
        # Normalizace osy rotace
        axis = axis / np.linalg.norm(axis) if np.linalg.norm(axis) > 0 else axis
        
        # Kosinová složka
        cos_angle = math.cos(angle)
        # Sinová složka
        sin_angle = math.sin(angle)
        
        # Rodriguesův vzorec pro rotaci vektoru
        rotated = vector * cos_angle + np.cross(axis, vector) * sin_angle + axis * np.dot(axis, vector) * (1 - cos_angle)
        
        # Aktualizace původního vektoru
        vector[:] = rotated / np.linalg.norm(rotated)

    def _create_cylinder_segment(self, start, end, radius, color, vertex_offset):
        """Vytvoří válcový segment mezi dvěma body"""
        # Směrový vektor
        direction = end - start
        height = np.linalg.norm(direction)
        if height < 1e-6:
            return  # Příliš krátký segment, přeskočíme
            
        direction = direction / height
        
        # Vytvoření kolmého vektoru na směr
        perpendicular = np.array([1.0, 0.0, 0.0]) if abs(direction[1]) > 0.9 else np.array([0.0, 1.0, 0.0])
        perpendicular = np.cross(perpendicular, direction)
        perpendicular = perpendicular / np.linalg.norm(perpendicular)
        
        # Druhý kolmý vektor pro kompletní souřadnicový systém
        perpendicular2 = np.cross(direction, perpendicular)
        
        # Počet segmentů válce po obvodu
        segments = 8
        
        # Vrcholy pro spodní a horní základnu válce
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            dx = math.cos(angle)
            dy = math.sin(angle)
            
            # Spodní základna
            point = start + radius * (perpendicular * dx + perpendicular2 * dy)
            self.vertices.extend([point[0], point[1], point[2], color[0], color[1], color[2], color[3]])
            
            # Horní základna
            point = end + radius * (perpendicular * dx + perpendicular2 * dy)
            self.vertices.extend([point[0], point[1], point[2], color[0], color[1], color[2], color[3]])
        
        # Indexy pro vykreslení trojúhelníků
        for i in range(segments):
            i0 = vertex_offset + i * 2
            i1 = vertex_offset + ((i + 1) % segments) * 2
            i2 = vertex_offset + i * 2 + 1
            i3 = vertex_offset + ((i + 1) % segments) * 2 + 1
            
            # Trojúhelníky pro plášť válce
            self.indices.extend([i0, i1, i2])
            self.indices.extend([i1, i3, i2])
            
            # Trojúhelníky pro spodní základnu
            if i < segments - 2:
                self.indices.extend([vertex_offset, vertex_offset + (i + 1) * 2, vertex_offset + (i + 2) * 2])
            
            # Trojúhelníky pro horní základnu
            if i < segments - 2:
                self.indices.extend([vertex_offset + 1, vertex_offset + (i + 2) * 2 + 1, vertex_offset + (i + 1) * 2 + 1])
