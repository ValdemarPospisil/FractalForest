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
        
        # Jehličí jako kužel
        needle_size = 0.25 - 0.03 * depth  # Menší jehličí na hlubších větvích
        
        # Vytvoření entity jehličí
        needle = Entity(
            parent=parent,
            model='cone',
            color=needle_color,
            position=Vec3(*position),
            scale=(needle_size, needle_size*2, needle_size),
            rotation=Quat().setFromAxisAngle(random.uniform(0, 360), Vec3(0, 1, 0))
        )
        
        # Přidáme několik jehliček kolem konce větve
        for _ in range(random.randint(3, 6)):
            offset = [random.uniform(-0.15, 0.15) for _ in range(3)]
            needle = Entity(
                parent=parent,
                model='cone',
                color=needle_color,
                position=Vec3(*(position + offset)),
                scale=(needle_size * 0.8, needle_size*1.8, needle_size * 0.8),
                rotation=Quat().setFromAxisAngle(random.uniform(0, 360), Vec3(0, 1, 0))
            )

    def _add_palm_leaves(self, parent, position):
        """
        Přidá palmové listy na konec kmene
        
        Parametry:
        - parent: rodičovská entita
        - position: pozice konce kmene
        """
        # Palmové listy jsou dlouhé a vycházejí z jednoho místa
        leaf_count = random.randint(6, 9)
        leaf_color = color.rgb(30, 120, 30)  # Zelená barva listů
        
        # Pozice mírně nad koncem kmene
        palm_top = position + np.array([0, 0.3, 0])
        
        # Přidání náhodnosti do barvy
        r_var = random.uniform(-self.color_variance, self.color_variance)
        g_var = random.uniform(-self.color_variance, self.color_variance)
        leaf_color = color.rgb(
            max(0, min(255, leaf_color[0] + r_var * 255)),
            max(0, min(255, leaf_color[1] + g_var * 255)),
            leaf_color[2]
        )
        
        # Vytvoření koruny palmy
        palm_crown = Entity(
            parent=parent,
            model='sphere',
            color=color.rgb(60, 40, 20),  # Hnědá barva pro základ listů
            position=Vec3(*palm_top),
            scale=0.3
        )
        
        # Vytvoření jednotlivých listů
        for i in range(leaf_count):
            # Úhel pro tento list
            angle = (i / leaf_count) * 360
            
            # Směr listu - vodorovně ven a mírně nahoru
            angle_rad = math.radians(angle)
            direction = np.array([
                math.cos(angle_rad),
                0.4 + random.uniform(-0.1, 0.1),  # Mírně nahoru s variací
                math.sin(angle_rad)
            ])
            direction = direction / np.linalg.norm(direction)
            
            # Délka listu
            leaf_length = 2.0 + random.uniform(-0.3, 0.3)
            
            # Konec listu
            leaf_end = palm_top + direction * leaf_length
            
            # Generování bodů podél listu pro křivku
            curve_points = []
            curve_segments = 8
            
            for j in range(curve_segments + 1):
                # Faktor pozice na listu (0 = začátek, 1 = konec)
                t = j / curve_segments
                
                # Pozice na přímce mezi začátkem a koncem
                linear_pos = palm_top + direction * (t * leaf_length)
                
                # Přidání zaoblení - list se prohýbá dolů
                bend_factor = 4.0 * t * (1 - t)  # Parabola s maximem v t=0.5
                bend_amount = 0.5  # Maximální prohnutí dolů
                
                # Aplikace prohnutí dolů
                bend_pos = linear_pos - np.array([0, bend_factor * bend_amount, 0])
                
                curve_points.append(bend_pos)
            
            # Tloušťka listu
            leaf_thickness = 0.08
            
            # Barva listu - trochu světlejší na konci
            end_leaf_color = color.rgb(
                leaf_color[0] + 20,
                leaf_color[1] + 20,
                leaf_color[2]
            )
            
            # Vytvoření segmentů listu
            for j in range(curve_segments):
                segment_start = curve_points[j]
                segment_end = curve_points[j+1]
                segment_length = np.linalg.norm(segment_end - segment_start)
                segment_center = (segment_start + segment_end) / 2
                
                # Výpočet směru segmentu
                segment_dir = segment_end - segment_start
                segment_dir = segment_dir / np.linalg.norm(segment_dir)
                
                # Barva segmentu - lineární přechod od začátku do konce
                segment_color = color.rgb(
                    leaf_color[0] + (end_leaf_color[0] - leaf_color[0]) * (j / curve_segments),
                    leaf_color[1] + (end_leaf_color[1] - leaf_color[1]) * (j / curve_segments),
                    leaf_color[2] + (end_leaf_color[2] - leaf_color[2]) * (j / curve_segments)
                )
                
                # Tloušťka se zmenšuje směrem ke konci
                segment_thickness = leaf_thickness * (1 - j/curve_segments * 0.7)
                
                # Výchozí cylindr v Ursině je orientován podél osy Y
                default_direction = np.array([0, 1, 0])
                
                # Výpočet rotace
                if np.isclose(np.abs(np.dot(segment_dir, default_direction)), 1.0, atol=1e-6):
                    rotation_quat = Quat()
                else:
                    axis = np.cross(default_direction, segment_dir)
                    axis = axis / np.linalg.norm(axis)
                    angle = np.arccos(np.dot(default_direction, segment_dir))
                    rotation_quat = Quat()
                    rotation_quat.setFromAxisAngle(angle, Vec3(*axis))
                
                # Vytvoření segmentu listu
                leaf_segment = Entity(
                    parent=parent,
                    model='cylinder',
                    color=segment_color,
                    position=Vec3(*segment_center),
                    scale=(segment_thickness, segment_length, segment_thickness * 0.5),  # Zploštělý válec
                    rotation=rotation_quat
                )
                
                # Pro první segment přidáme i boční listy
                if j < 3 and j % 2 == 0:
                    # Přidání bočních lístků kolmo k hlavnímu listu
                    self._add_palm_leaflets(parent, segment_center, segment_dir, segment_thickness, leaf_color)

    def _add_palm_leaflets(self, parent, position, main_direction, thickness, base_color):
        """
        Přidá boční lístky na palmový list
        
        Parametry:
        - parent: rodičovská entita
        - position: pozice na hlavním listu
        - main_direction: směr hlavního listu
        - thickness: tloušťka hlavního listu
        - base_color: základní barva
        """
        # Počet lístků na každé straně
        leaflet_count = random.randint(3, 5)
        
        # Nalezení směru kolmého k hlavnímu listu
        up_vector = np.array([0, 1, 0])
        side_vector = np.cross(main_direction, up_vector)
        side_vector = side_vector / np.linalg.norm(side_vector)
        
        for i in range(leaflet_count):
            # Vytvořím lístky na obou stranách
            for side in [-1, 1]:
                # Pozice lístku - mírně odsazené od hlavního listu
                side_pos = position + side_vector * side * thickness * 1.2
                
                # Směr lístku - kolmo od hlavního listu a mírně dopředu
                side_dir = side_vector * side + main_direction * 0.3
                side_dir = side_dir / np.linalg.norm(side_dir)
                
                # Délka lístku
                leaflet_length = 0.3 + random.uniform(-0.05, 0.05)
                
                # Konec lístku
                leaflet_end = side_pos + side_dir * leaflet_length
                
                # Střed lístku
                leaflet_center = (side_pos + leaflet_end) / 2
                
                # Tloušťka lístku
                leaflet_thickness = thickness * 0.4
                
                # Barva lístku - trochu světlejší
                leaflet_color = color.rgb(
                    min(255, base_color[0] + 15),
                    min(255, base_color[1] + 15),
                    base_color[2]
                )
                
                # Výchozí cylindr v Ursině je orientován podél osy Y
                default_direction = np.array([0, 1, 0])
                
                # Výpočet rotace
                if np.isclose(np.abs(np.dot(side_dir, default_direction)), 1.0, atol=1e-6):
                    rotation_quat = Quat()
                else:
                    axis = np.cross(default_direction, side_dir)
                    axis = axis / np.linalg.norm(axis)
                    angle = np.arccos(np.dot(default_direction, side_dir))
                    rotation_quat = Quat()
                    rotation_quat.setFromAxisAngle(angle, Vec3(*axis))
                
                # Vytvoření lístku
                leaflet = Entity(
                    parent=parent,
                    model='cylinder',
                    color=leaflet_color,
                    position=Vec3(*leaflet_center),
                    scale=(leaflet_thickness, leaflet_length, leaflet_thickness * 0.3),  # Zploštělý válec
                    rotation=rotation_quat
                )

    # Konverze moderngl meshe na Ursina mesh
    def convert_mesh_to_ursina(self):
        """
        Převede interní geometrii na Ursina Mesh
        
        Vrací:
        - objekt Mesh pro použití v Ursina
        """
        # Pro vytvoření Ursina mesh potřebujeme:
        # 1. Vrcholy
        # 2. Trojúhelníky (indexy)
        # 3. UV koordináty (můžeme použít výchozí)
        # 4. Normály
        
        if not hasattr(self, 'vertices') or len(self.branches) == 0:
            logger.warning("Pokus o konverzi prázdného meshe!")
            return None
        
        # Pro každou větev vytvoříme válec
        vertices = []
        triangles = []
        uvs = []
        normals = []
        
        vertex_index = 0
        
        for branch in self.branches:
            start_pos = branch['start']
            end_pos = branch['end']
            radius = branch['radius']
            
            # Výpočet směru válce
            direction = end_pos - start_pos
            direction_length = np.linalg.norm(direction)
            if direction_length < 0.0001:
                continue
            
            direction = direction / direction_length
            
            # Vytvoření kolmého vektoru
            perpendicular = np.array([1.0, 0.0, 0.0])
            if abs(np.dot(direction, perpendicular)) > 0.9:
                perpendicular = np.array([0.0, 1.0, 0.0])
            
            # Nalezení dvou kolmých vektorů pro vytvoření kruhu
            perpendicular = perpendicular - direction * np.dot(direction, perpendicular)
            perpendicular = perpendicular / np.linalg.norm(perpendicular)
            
            binormal = np.cross(direction, perpendicular)
            binormal = binormal / np.linalg.norm(binormal)
            
            # Počet segmentů po obvodu
            segments = 8
            
            # Vytvoření kruhu na začátku a na konci
            for end in [0, 1]:
                pos = start_pos if end == 0 else end_pos
                
                for i in range(segments):
                    angle = 2 * math.pi * i / segments
                    
                    # Pozice vrcholu na kružnici
                    offset = perpendicular * math.cos(angle) + binormal * math.sin(angle)
                    vertex = pos + offset * radius
                    
                    vertices.append(vertex)
                    
                    # Normála - směřuje ven od osy válce
                    normal = offset  # Již normalizovaný
                    normals.append(normal)
                    
                    # UV koordináty (jednoduché mapování)
                    u = i / segments
                    v = end
                    uvs.append(np.array([u, v]))
            
            # Vytvoření trojúhelníků mezi začátkem a koncem
            for i in range(segments):
                i1 = vertex_index + i
                i2 = vertex_index + (i + 1) % segments
                i3 = vertex_index + i + segments
                i4 = vertex_index + (i + 1) % segments + segments
                
                # Dva trojúhelníky tvoří jeden obdélník
                triangles.append([i1, i2, i3])
                triangles.append([i2, i4, i3])
            
            vertex_index += segments * 2
        
        # Převod na numpy pole pro Ursina
        vertices = np.array(vertices, dtype=np.float32)
        triangles = np.array(triangles, dtype=np.int32)
        uvs = np.array(uvs, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        
        # Vytvoření Ursina Mesh
        return Mesh(
            vertices=vertices, 
            triangles=triangles,
            uvs=uvs,
            normals=normals
        )
