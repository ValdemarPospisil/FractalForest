# generation/lsystem.py
import math
import random
import numpy as np

class LSystem:
    """Třída pro implementaci L-systému a generování geometrie."""
    def __init__(self, axiom, rules, angle, scale, initial_length=0.1, initial_width=0.03):
        self.axiom = axiom
        self.rules = rules
        # Přidání malé náhodnosti k úhlu a škále pro variabilitu
        self.angle = angle + random.uniform(-math.radians(3), math.radians(3))
        self.scale = scale * random.uniform(0.95, 1.05)
        self.initial_length = initial_length
        self.initial_width = initial_width
        self.current_string = axiom
        self.iterations = 0 # Přidáno pro sledování iterací

    def generate(self, iterations):
        """Generuje řetězec L-systému po zadaný počet iterací."""
        self.iterations = iterations
        current = self.axiom
        for _ in range(iterations):
            next_gen = ""
            for char in current:
                # Stochastické pravidlo - možnost nahradit F i něčím jiným s malou pravděpodobností
                if char == 'F' and random.random() < 0.02: # Malá šance na změnu
                    next_gen += random.choice(["F", "FF", "F[+F]F[-F]F"]) # Příklad variace
                elif char in self.rules:
                    next_gen += self.rules[char]
                else:
                    next_gen += char
            current = next_gen
        self.current_string = current
        return current

    def get_vertices(self):
        """Převádí vygenerovaný řetězec na posloupnost vrcholů a barev pro vykreslení."""
        vertices = []
        colors = []

        stack = []
        position = np.array([0.0, -0.8, 0.0], dtype='f4') # Začátek kmene
        direction = np.array([0.0, 1.0, 0.0], dtype='f4') # Směr nahoru
        # Délka se může lišit v závislosti na iteracích a scale
        branch_length = self.initial_length * (self.scale ** (self.iterations / 2)) # Upravená délka
        branch_width = self.initial_width # Šířka se může také měnit, ale pro jednoduchost necháme

        # Barvy
        trunk_color = np.array([0.55, 0.27, 0.07], dtype='f4') # Hnědá
        leaf_color = np.array([0.0, random.uniform(0.6, 0.9), 0.0], dtype='f4') # Mírně náhodná zelená

        for char in self.current_string:
            if char == 'F': # Kresli vpřed
                start = position.copy()
                end = position + direction * branch_length

                # Jednoduchá čára pro segment
                vertices.extend(start)
                vertices.extend(end)
                colors.extend(trunk_color)
                colors.extend(trunk_color)

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
                # Při větvení zmenšíme délku
                stack.append((position.copy(), direction.copy(), branch_length))
                branch_length *= self.scale
            elif char == ']': # Obnov stav
                if stack: # Zajistíme, že stack není prázdný
                    position, direction, branch_length = stack.pop()
                else:
                    print("Warning: Trying to pop from an empty stack.") # Debugging

            elif char == 'X': # X reprezentuje list nebo koncový bod
                # Můžeme zde přidat geometrii listu, pro jednoduchost necháme jako koncový bod
                # Nebo přidáme krátký zelený segment jako náznak listu
                 start = position.copy()
                 leaf_size = branch_length * 0.5 # Velikost "listu"
                 # Náhodný směr pro list
                 leaf_dir = direction + np.random.uniform(-0.3, 0.3, 3)
                 norm = np.linalg.norm(leaf_dir)
                 if norm > 1e-6: # Zabráníme dělení nulou
                    leaf_dir /= norm
                 else:
                     leaf_dir = direction # Fallback

                 end = position + leaf_dir * leaf_size

                 vertices.extend(start)
                 vertices.extend(end)
                 colors.extend(trunk_color) # Konec větve je ještě hnědý
                 colors.extend(leaf_color) # "List" je zelený

        if not vertices: # Pokud by se nic nevygenerovalo
             return np.array([], dtype='f4'), np.array([], dtype='f4')

        return np.array(vertices, dtype='f4').flatten(), np.array(colors, dtype='f4').flatten()

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
