"""
Implementace stromu využívající L-systém
"""
import logging
import random
import math
import numpy as np
from ursina import *

logger = logging.getLogger(__name__)

class Tree:
    """
    Třída reprezentující 3D strom
    """
    def __init__(self, instructions, angle=25.0, length=1.0, tree_type="pine"):
        """
        Inicializace stromu
        
        Parametry:
        - instructions: řetězec s instrukcemi z L-systému
        - angle: úhel natočení v stupních
        - length: délka segmentu větve
        - tree_type: typ stromu
        """
        self.instructions = instructions
        self.angle = angle
        self.length = length
        self.tree_type = tree_type
        
        # Parametry pro různé části stromu
        self.trunk_radius = 0.1
        self.radius_decay = 0.75  # Jak rychle se zužují větve
        self.color_variance = 0.1  # Variance barvy
        
        # Analýza stromu
        self.height = 0
        self.branch_count = 0
        
        # Seznam větví (pro pozdější vytvoření entit)
        self.branches = []
        
        # Interpretace instrukcí a vytvoření větví
        self._interpret_instructions()
        
    def _interpret_instructions(self):
        """
        Interpretuje instrukce L-systému a vytváří segmenty stromu
        """
        logger.debug(f"Interpretace instrukcí L-systému, délka: {len(self.instructions)}")
        
        # Počáteční pozice a orientace
        position = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 1.0, 0.0])  # Směr nahoru (Y+)
        
        # Vytvoření rotačních matic
        rotation_matrix_left = self._create_rotation_matrix(self.angle)
        rotation_matrix_right = self._create_rotation_matrix(-self.angle)
        
        # Kořenoví běžci budou mít menší úhel větvení
        rotation_matrix_shallow_left = self._create_rotation_matrix(self.angle / 2)
        rotation_matrix_shallow_right = self._create_rotation_matrix(-self.angle / 2)
        
        # Zásobník pro větvení
        stack = []
        current_radius = self.trunk_radius
        
        # Interpretace instrukcí
        depth = 0
        max_depth = 0
        
        for i, char in enumerate(self.instructions):
            if char == 'F':  # Kresba větve
                # Aktuální pozice
                start_pos = position.copy()
                
                # Posun ve směru
                position = position + direction * self.length
                
                # Zjištění maximální výšky
                self.height = max(self.height, position[1])
                
                # Přidání větve
                self.branches.append({
                    'start': start_pos,
                    'end': position.copy(),
                    'radius': current_radius,
                    'depth': depth
                })
                
                # Počítání větví
                self.branch_count += 1
                
            elif char == '+':  # Rotace doleva
                direction = np.dot(rotation_matrix_left, direction)
            elif char == '-':  # Rotace doprava
                direction = np.dot(rotation_matrix_right, direction)
            elif char == '&':  # Mělká rotace doleva (pro kořenové běžce)
                direction = np.dot(rotation_matrix_shallow_left, direction)
            elif char == '^':  # Mělká rotace doprava
                direction = np.dot(rotation_matrix_shallow_right, direction)
            elif char == '[':  # Uložení pozice a orientace
                stack.append((position.copy(), direction.copy(), current_radius, depth))
                depth += 1
                max_depth = max(max_depth, depth)
                current_radius *= self.radius_decay  # Zmenšení poloměru pro nové větve
            elif char == ']':  # Obnovení pozice a orientace
                position, direction, current_radius, depth = stack.pop()
        
        logger.debug(f"Dokončena interpretace. Větví: {self.branch_count}, Výška: {self.height}")
        
    def _create_rotation_matrix(self, angle_degrees):
        """
        Vytvoření rotační matice kolem osy Z
        
        Parametry:
        - angle_degrees: úhel ve stupních
        
        Vrací:
        - 3x3 rotační matice
        """
        # Konverze na radiány
        angle_rad = math.radians(angle_degrees)
        
        # Rotace kolem Z
        # [cos(a) -sin(a) 0]
        # [sin(a)  cos(a) 0]
        # [0       0      1]
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        return np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a,  0],
            [0,     0,      1]
        ])
    
    def create_entity(self, color=color.rgb(76, 153, 76)):
        """
        Vytvoří 3D entitu stromu v Ursině
        
        Parametry:
        - color: základní barva stromu
        
        Vrací:
        - kořenová entita stromu
        """
        # Vytvoření kořenové entity, ke které budou připojeny všechny části stromu
        root_entity = Entity()
        
        # Vytvoření jednotlivých větví jako válcovitých entit
        for i, branch in enumerate(self.branches):
            # Spočítání délky segmentu
            segment_start = branch['start']
            segment_end = branch['end']
            segment_length = np.linalg.norm(segment_end - segment_start)
            
            # Spočítání pozice středu segmentu
            segment_center = (segment_start + segment_end) / 2
            
            # Variace barvy podle hloubky
            depth_factor = min(branch['depth'] / 5.0, 1.0)
            branch_color = self._get_branch_color(depth_factor, color)
            
            # Výpočet rotace větve (směr od start do end)
            direction = segment_end - segment_start
            direction = direction / np.linalg.norm(direction)
            
            # Výchozí cylindr v Ursině je orientován podél osy Y
            # Musíme najít rotaci z (0,1,0) na náš směr
            default_direction = np.array([0, 1, 0])
            
            # Speciální případ - pokud směr je téměř shodný s výchozím, není potřeba rotace
            if np.isclose(np.abs(np.dot(direction, default_direction)), 1.0, atol=1e-6):
                rotation_quat = Quat()
            else:
                # Výpočet křížového produktu dává osu rotace
                axis = np.cross(default_direction, direction)
                axis = axis / np.linalg.norm(axis)
                
                # Úhel mezi vektory
                angle = np.arccos(np.dot(default_direction, direction))
                
                # Vytvoření quaternionu pro tuto rotaci
                rotation_quat = Quat()
                rotation_quat.setFromAxisAngle(angle, Vec3(*axis))
            
            # Vytvoření cylindru pro větev
            branch_radius = branch['radius'] * (1.0 - 0.1 * random.random())  # Malá náhodnost
            
            # Úprava parametrů větve podle typu stromu
            if self.tree_type == "pine" and branch['depth'] > 0:
                # Jehličnan - tenčí a tmavší větve
                branch_radius *= 0.8
            elif self.tree_type == "oak" and branch['depth'] > 0:
                # Dub - silnější větve
                branch_radius *= 1.1
            elif self.tree_type == "palm" and branch['depth'] == 0:
                # Palma - silnější kmen
                branch_radius *= 1.3
            
            # Vytvoření entity větve
            branch_entity = Entity(
                parent=root_entity,
                model='cylinder',
                color=branch_color,
                position=Vec3(*segment_center),
                scale=(branch_radius*2, segment_length, branch_radius*2),
                rotation=rotation_quat
            )
            
            # Pro listnaté stromy a keře přidáme listy na koncích větví
            if (self.tree_type in ["oak", "bush", "willow"] and 
                branch['depth'] > 0 and 
                i % 3 == 0):  # Jen na některých větvích
                self._add_leaves(root_entity, segment_end, branch['depth'])
                
            # Pro jehličnany přidáme jehličí
            if self.tree_type == "pine" and branch['depth'] > 0:
                if i % 2 == 0:  # Jen na některých větvích
                    self._add_pine_needles(root_entity, segment_end, branch['depth'])
        
        # Pro palmy přidáme na konec kmene palmové listy
        if self.tree_type == "palm":
            # Najdeme konec kmene
            for branch in self.branches:
                if branch['depth'] == 0:  # Hlavní kmen
                    self._add_palm_leaves(root_entity, branch['end'])
        
        return root_entity
    
    def _get_branch_color(self, depth_factor, base_color):
        """
        Získá barvu větve podle hloubky v stromu
        
        Parametry:
        - depth_factor: faktor hloubky (0-1)
        - base_color: základní barva 
        
        Vrací:
        - barva pro danou větev
        """
        if self.tree_type == "pine":
            # Pro jehličnany - tmavý kmen, světlejší větvičky
            trunk_color = color.rgb(60, 30, 15)  # Tmavě hnědá
            leaf_color = base_color
            
            # Lineární interpolace mezi barvami
            r = trunk_color[0] * (1-depth_factor) + leaf_color[0] * depth_factor
            g = trunk_color[1] * (1-depth_factor) + leaf_color[1] * depth_factor
            b = trunk_color[2] * (1-depth_factor) + leaf_color[2] * depth_factor
            
            return color.rgb(r, g, b)
        elif self.tree_type == "oak":
            # Pro duby - světlejší kmen
            return color.rgb(90 - 20 * depth_factor, 
                             50 + 20 * depth_factor, 
                             30)
        elif self.tree_type == "palm":
            # Pro palmy - specifický odstín kmene
            return color.rgb(120 - 30 * depth_factor, 
                             90 - 20 * depth_factor, 
                             60 - 10 * depth_factor)
        else:
            # Výchozí barevné schéma
            return color.rgb(76 - 30 * depth_factor, 
                             51 + 40 * depth_factor, 
                             25)
    
    def _add_leaves(self, parent, position, depth):
        """
        Přidá listy na konec větve
        
        Parametry:
        - parent: rodičovská entita
        - position: pozice konce větve
        - depth: hloubka větvení
        """
        leaf_size = 0.3 - 0.05 * depth  # Menší listy na hlubších větvích
        
        # Základní barva listů podle typu stromu
        if self.tree_type == "oak":
            leaf_color = color.rgb(60, 128, 30)
        elif self.tree_type == "willow":
            leaf_color = color.rgb(150, 190, 60)
        elif self.tree_type == "bush":
            leaf_color = color.rgb(50, 180, 50)
        else:
            leaf_color = color.rgb(50, 150, 50)
        
        # Přidání náhodnosti do barvy
        r_var = random.uniform(-self.color_variance, self.color_variance)
        g_var = random.uniform(-self.color_variance, self.color_variance)
        leaf_color = color.rgb(
            max(0, min(255, leaf_color[0] + r_var * 255)),
            max(0, min(255, leaf_color[1] + g_var * 255)),
            leaf_color[2]
        )
        
        # Vytvoření entity listu
        leaf = Entity(
            parent=parent,
            model='sphere',
            color=leaf_color,
            position=Vec3(*position),
            scale=leaf_size
        )
        
        # Pro některé typy přidáme více listů
        if self.tree_type in ["oak", "bush"]:
            # Přidáme 2-3 další listy blízko
            for _ in range(random.randint(2, 3)):
                offset = [random.uniform(-0.2, 0.2) for _ in range(3)]
                
                # Pro keře větší variabilita v barvě
                if self.tree_type == "bush":
                    r_var = random.uniform(-self.color_variance*2, self.color_variance*2)
                    g_var = random.uniform(-self.color_variance*2, self.color_variance*2)
                    leaf_color = color.rgb(
                        max(0, min(255, leaf_color[0] + r_var * 255)),
                        max(0, min(255, leaf_color[1] + g_var * 255)),
                        leaf_color[2]
                    )
                
                leaf = Entity(
                    parent=parent,
                    model='sphere',
                    color=leaf_color,
                    position=Vec3(*(position + offset)),
                    scale=leaf_size * random.uniform(0.8, 1.2)
                )
    
    def _add_pine_needles(self, parent, position, depth):
        """
        Přidá jehličí na konec větve
        
        Parametry:
        - parent: rodičovská entita
        - position: pozice konce větve
        - depth: hloubka větvení
        """
        # Základní barva jehličí
        needle_color = color.rgb(10, 80, 30)  # Tmavě zelená
        
        # Přidání náhodnosti do barvy
        r_var = random.uniform(-self.color_variance, self.color_variance)
        g_var = random.uniform(-self.color_variance, self.color_variance)
        needle_color = color.rgb(
            max(0, min(255, needle_color[0] + r_var * 255)),
            max(0, min(255, needle_color[1] + g_var * 255)),
            needle_color[2]
        )
