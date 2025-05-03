import math
import random
import numpy as np
import logging

class LSystem:
    """Třída pro implementaci L-systému a generování geometrie."""
    def __init__(self, axiom, rules, angle, scale, initial_length=0.1, initial_width=0.03,
                 trunk_color=(0.55, 0.27, 0.07), leaf_color=(0.0, 0.8, 0.0)):
        self.axiom = axiom
        self.rules = rules
        # Přidání malé náhodnosti k úhlu a škále pro variabilitu
        self.angle = angle + random.uniform(-math.radians(3), math.radians(3))
        self.scale = scale * random.uniform(0.95, 1.05)
        self.initial_length = initial_length
        self.initial_width = initial_width
        self.trunk_color = np.array(trunk_color, dtype='f4')
        
        # Náhodnost v barvě listů pro větší variabilitu
        if isinstance(leaf_color, tuple):
            self.leaf_color = np.array(leaf_color, dtype='f4')
        else:
            # Pokud je zadán rozsah barev, vybereme náhodnou barvu
            leaf_min, leaf_max = leaf_color
            self.leaf_color = np.array([
                random.uniform(leaf_min[0], leaf_max[0]),
                random.uniform(leaf_min[1], leaf_max[1]),
                random.uniform(leaf_min[2], leaf_max[2])
            ], dtype='f4')
        
        self.current_string = axiom
        self.iterations = 0 # Přidáno pro sledování iterací
        logging.debug(f"LSystem initialized with angle={math.degrees(self.angle):.1f}°, scale={self.scale:.2f}")

    def generate(self, iterations):
        """Generuje řetězec L-systému po zadaný počet iterací."""
        self.iterations = iterations
        current = self.axiom
        logging.debug(f"Starting L-system generation with axiom: {self.axiom}")
        
        for i in range(iterations):
            next_gen = ""
            for char in current:
                # Stochastické pravidlo - možnost nahradit F i něčím jiným s malou pravděpodobností
                if char == 'F' and random.random() < 0.02: # Malá šance na změnu
                    variation = random.choice(["F", "FF", "F[+F]F[-F]F"])
                    next_gen += variation
                    logging.debug(f"Applied stochastic rule on F: {variation}")
                elif char in self.rules:
                    next_gen += self.rules[char]
                else:
                    next_gen += char
            current = next_gen
            logging.debug(f"Generation {i+1} complete, string length: {len(current)}")
            
        self.current_string = current
        logging.info(f"L-system string generated with {iterations} iterations, final length: {len(self.current_string)}")
        return current

    def get_vertices(self):
        """Převádí vygenerovaný řetězec na posloupnost vrcholů a barev pro vykreslení."""
        vertices = []
        colors = []
        normals = []  # Přidáváme normály pro lepší osvětlení

        stack = []
        # Upraveno - začátek kmene je nyní přesně ve středu
        position = np.array([0.0, -0.5, 0.0], dtype='f4') # Začátek kmene
        direction = np.array([0.0, 1.0, 0.0], dtype='f4') # Směr nahoru
        # Délka se může lišit v závislosti na iteracích a scale
        branch_length = self.initial_length * (self.scale ** (self.iterations / 2)) # Upravená délka
        branch_width = self.initial_width # Šířka se může také měnit, ale pro jednoduchost necháme

        # Pro sledování hierarchie větvení - použijeme pro výpočet barev
        branch_depth = 0
        max_branch_depth = 6  # Omezení pro barevný gradient

        for char in self.current_string:
            if char == 'F': # Kresli vpřed
                start = position.copy()
                end = position + direction * branch_length

                # Jednoduchá čára pro segment
                vertices.extend(start)
                vertices.extend(end)
                
                # Výpočet barvy na základě tloušťky větve (hloubky větvení)
                segment_color = self._compute_segment_color(branch_depth, max_branch_depth)
                colors.extend(segment_color)
                colors.extend(segment_color)
                
                # Výpočet normály pro daný segment
                segment_normal = self._compute_normal(direction)
                normals.extend(segment_normal)
                normals.extend(segment_normal)
                
                position = end # Aktualizace pozice

            elif char == '+': # Otoč doleva (kolem Y)
                direction = self._rotate_y(direction, self.angle)
            elif char == '-': # Otoč doprava (kolem Y)
                direction = self._rotate_y(direction, -self.angle)
            elif char == '&': # Otoč dolů (kolem X)
                direction = self._rotate_x(direction, self.angle)
            elif char == '^': # Otoč nahoru (kolem X)
                direction = self._rotate_x(direction, -self.angle)
            elif char == '\\': # Otoč doprava (kolem Z)
                direction = self._rotate_z(direction, self.angle)
            elif char == '/': # Otoč doleva (kolem Z)
                direction = self._rotate_z(direction, -self.angle)

            elif char == '[': # Ulož stav
                # Při větvení zmenšíme délku a zvýšíme hloubku větvení
                stack.append((position.copy(), direction.copy(), branch_length, branch_depth))
                branch_length *= self.scale
                branch_depth += 1  # Zvýšíme hloubku větvení
            elif char == ']': # Obnov stav
                if stack: # Zajistíme, že stack není prázdný
                    position, direction, branch_length, branch_depth = stack.pop()
                else:
                    logging.warning("Trying to pop from an empty stack.")

            elif char == 'X': # X reprezentuje list nebo koncový bod
                # Přidáme list jako krátký zelený segment
                start = position.copy()
                
                # Náhodný směr pro list s větší variabilitou
                leaf_dir = direction.copy()
                # Rotace okolo náhodné osy pro různé natočení listů
                random_angle = random.uniform(-math.pi/3, math.pi/3)  # Větší rozsah úhlů
                random_axis = random.choice(['x', 'y', 'z'])
                if random_axis == 'x':
                    leaf_dir = self._rotate_x(leaf_dir, random_angle)
                elif random_axis == 'y':
                    leaf_dir = self._rotate_y(leaf_dir, random_angle)
                else:
                    leaf_dir = self._rotate_z(leaf_dir, random_angle)
                
                # Velikost listu závisí na hloubce větvení
                leaf_size = branch_length * (1.0 + 0.5 * branch_depth / max_branch_depth)
                end = position + leaf_dir * leaf_size
                
                # Přidáme list do geometrie
                vertices.extend(start)
                vertices.extend(end)
                
                # Přechod barvy od kmene k listu
                transition_color = self._compute_leaf_transition_color(branch_depth, max_branch_depth)
                colors.extend(transition_color)
                colors.extend(self.leaf_color)
                
                # Normála pro list
                leaf_normal = self._compute_normal(leaf_dir)
                normals.extend(leaf_normal)
                normals.extend(leaf_normal)

        if not vertices: # Pokud by se nic nevygenerovalo
            logging.warning("No vertices generated from L-system string")
            return np.array([], dtype='f4'), np.array([], dtype='f4'), np.array([], dtype='f4')

        return np.array(vertices, dtype='f4').flatten(), np.array(colors, dtype='f4').flatten(), np.array(normals, dtype='f4').flatten()

    def _compute_segment_color(self, depth, max_depth):
        """Vypočítá barvu segmentu na základě hloubky větvení."""
        # Základní barva kmene
        trunk_color = np.array(self.trunk_color)
        
        # Čím vyšší větvení, tím světlejší odstín
        color_factor = min(depth / max_depth, 1.0)
        
        # Postupný přechod barvy směrem ke koncům větví
        # Světlejší a teplejší odstíny pro tenčí větve
        color_shift = np.array([0.2, 0.08, 0.02]) * color_factor
        color = trunk_color + color_shift
        
        # Ujistíme se, že barva zůstává v rozsahu 0-1
        return np.clip(color, 0.0, 1.0)
    
    def _compute_leaf_transition_color(self, depth, max_depth):
        """Vypočítá přechodovou barvu mezi kmenem a listem."""
        trunk_color = np.array(self.trunk_color)
        leaf_color = np.array(self.leaf_color)
        
        # Míra přechodu závisí na hloubce
        transition = min(0.3 + depth / max_depth * 0.7, 1.0)
        
        # Lineární interpolace mezi barvou kmene a listu
        color = trunk_color * (1 - transition) + leaf_color * transition
        
        return np.clip(color, 0.0, 1.0)
    
    def _compute_normal(self, direction):
        """Vypočítá normálu kolmou na směr větve."""
        # Preferovaný způsob výpočtu normály závisí na směru větve
        up = np.array([0.0, 1.0, 0.0], dtype='f4')
        
        # Normálový vektor kolmý na směr větve a světový nahoru
        cross = np.cross(direction, up)
        norm_cross = np.linalg.norm(cross)
        
        if norm_cross < 1e-6:  # Téměř paralelní s osou Y
            # Použijeme osu X jako alternativní vektor pro výpočet
            cross = np.cross(direction, np.array([1.0, 0.0, 0.0], dtype='f4'))
            norm_cross = np.linalg.norm(cross)
            
            if norm_cross < 1e-6:  # I tohle selhalo
                # Poslední možnost - použijeme Z osu
                cross = np.cross(direction, np.array([0.0, 0.0, 1.0], dtype='f4'))
                norm_cross = np.linalg.norm(cross)
                
                if norm_cross < 1e-6:  # Pro případ totálního selhání (nemělo by nastat)
                    return np.array([1.0, 0.0, 0.0], dtype='f4')
        
        # Normalizace a návrat normály
        return cross / norm_cross

    def _rotate_y(self, direction, angle):
        """Rotace vektoru kolem osy Y."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotation_matrix = np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ], dtype='f4')
        return np.dot(rotation_matrix, direction)

    def _rotate_x(self, direction, angle):
        """Rotace vektoru kolem osy X."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, cos_a, -sin_a],
            [0, sin_a, cos_a]
        ], dtype='f4')
        return np.dot(rotation_matrix, direction)

    def _rotate_z(self, direction, angle):
        """Rotace vektoru kolem osy Z."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotation_matrix = np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ], dtype='f4')
        return np.dot(rotation_matrix, direction)
