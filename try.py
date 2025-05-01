import moderngl
import numpy as np
import glfw
from pyrr import Matrix44
import math
import random

# Třída pro implementaci L-systému
class LSystem:
    def __init__(self, axiom, rules, angle, scale):
        self.axiom = axiom
        self.rules = rules
        self.angle = angle  # Úhel otáčení v radiánech
        self.scale = scale  # Škálování délky větví s každou iterací
        self.current_string = axiom
    
    def generate(self, iterations):
        """Generuje řetězec L-systému po zadaný počet iterací"""
        current = self.axiom
        for _ in range(iterations):
            next_gen = ""
            for char in current:
                if char in self.rules:
                    next_gen += self.rules[char]
                else:
                    next_gen += char
            current = next_gen
        self.current_string = current
        return current
    
    def get_vertices(self):
        """Převádí vygenerovaný řetězec na posloupnost vrcholů pro vykreslení"""
        vertices = []
        colors = []
        
        # Stack pro ukládání pozic a směrů
        stack = []
        position = [0.0, -0.8, 0.0]  # Začátek kmene u spodního okraje obrazovky
        direction = [0.0, 1.0, 0.0]  # Směr nahoru
        branch_length = 0.1  # Počáteční délka větve
        branch_width = 0.03  # Šířka kmene
        
        # Barvy pro kmen a listy
        trunk_color = [0.55, 0.27, 0.07]  # Hnědá
        leaf_color = [0.0, 0.8, 0.0]      # Zelená
        
        for char in self.current_string:
            if char == 'F':  # Kresli vpřed
                # Počáteční bod
                start = position.copy()
                
                # Koncový bod
                end = [
                    position[0] + direction[0] * branch_length,
                    position[1] + direction[1] * branch_length,
                    position[2] + direction[2] * branch_length
                ]
                
                # Přidáme segment větve (jednoduchá čára pro začátek)
                vertices.extend(start)
                vertices.extend(end)
                
                # Přidáme barvy - kmeny jsou hnědé
                colors.extend(trunk_color)
                colors.extend(trunk_color)
                
                # Aktualizace pozice
                position = end
                
            elif char == '+':  # Otoč doleva (v XY rovině)
                direction = self._rotate_y(direction, self.angle)
                
            elif char == '-':  # Otoč doprava (v XY rovině)
                direction = self._rotate_y(direction, -self.angle)
                
            elif char == '&':  # Otoč dolů (v XZ rovině)
                direction = self._rotate_x(direction, self.angle)
                
            elif char == '^':  # Otoč nahoru (v XZ rovině)
                direction = self._rotate_x(direction, -self.angle)
                
            elif char == '\\':  # Otoč doprava (v YZ rovině)
                direction = self._rotate_z(direction, self.angle)
                
            elif char == '/':  # Otoč doleva (v YZ rovině)
                direction = self._rotate_z(direction, -self.angle)
                
            elif char == '[':  # Ulož stav
                stack.append((position.copy(), direction.copy(), branch_length, branch_width))
                # Při větvení lehce zmenšíme délku a šířku větví
                branch_length *= self.scale
                branch_width *= self.scale
                
            elif char == ']':  # Obnov stav
                position, direction, branch_length, branch_width = stack.pop()
                
            elif char == 'X':  # X reprezentuje list na konci větve
                # Přidáme list jako malý segment s jinou barvou
                start = position.copy()
                leaf_size = branch_length * 0.8
                
                # Vytvoříme malý náhodný posun pro list
                leaf_dir = [
                    direction[0] + (random.random() - 0.5) * 0.2,
                    direction[1] + (random.random() - 0.5) * 0.2,
                    direction[2] + (random.random() - 0.5) * 0.2
                ]
                
                # Normalizace směru
                length = math.sqrt(sum(d*d for d in leaf_dir))
                if length > 0:
                    leaf_dir = [d/length for d in leaf_dir]
                
                end = [
                    position[0] + leaf_dir[0] * leaf_size,
                    position[1] + leaf_dir[1] * leaf_size,
                    position[2] + leaf_dir[2] * leaf_size
                ]
                
                vertices.extend(start)
                vertices.extend(end)
                
                # Přidáme barvy - listy jsou zelené
                colors.extend(trunk_color)
                colors.extend(leaf_color)
        
        return np.array(vertices, dtype='f4'), np.array(colors, dtype='f4')
        
    def _rotate_y(self, direction, angle):
        """Rotace kolem osy Y"""
        x, y, z = direction
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return [x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a]
    
    def _rotate_x(self, direction, angle):
        """Rotace kolem osy X"""
        x, y, z = direction
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return [x, y * cos_a - z * sin_a, y * sin_a + z * cos_a]
    
    def _rotate_z(self, direction, angle):
        """Rotace kolem osy Z"""
        x, y, z = direction
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return [x * cos_a - y * sin_a, x * sin_a + y * cos_a, z]


# Inicializace GLFW a ModernGL
def initialize_window():
    # Inicializace GLFW
    if not glfw.init():
        raise RuntimeError("Nelze inicializovat GLFW")
    
    # Nastavení OpenGL verze
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    
    # Vytvoření okna
    width, height = 800, 600
    window = glfw.create_window(width, height, "L-System Tree", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Nelze vytvořit GLFW okno")
    
    # Nastavení okna jako aktuálního kontextu
    glfw.make_context_current(window)
    
    # Vytvoření ModernGL kontextu
    ctx = moderngl.create_context()
    
    return window, ctx, width, height


# Vertex shader
VERTEX_SHADER = """
#version 330
in vec3 in_position;
in vec3 in_color;

out vec3 color;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main() {
    gl_Position = projection * view * model * vec4(in_position, 1.0);
    color = in_color;
}
"""

# Fragment shader
FRAGMENT_SHADER = """
#version 330
in vec3 color;
out vec4 fragColor;

void main() {
    fragColor = vec4(color, 1.0);
}
"""

def main():
    # Parametry L-systému pro strom
    # Axiom: Počáteční řetězec
    # Pravidla: Definice jak se každý symbol rozvine v další iteraci
    axiom = "X"
    rules = {
        "X": "F[-X][+X][/X][\\X]",  # X se rozvine do více větví
        "F": "FF"                    # F (segment větve) se prodlouží
    }
    angle = math.radians(25)  # Úhel mezi větvemi
    scale = 0.8               # Zmenšování délky větví s každou úrovní
    
    # Vytvoření L-systému
    lsystem = LSystem(axiom, rules, angle, scale)
    
    # Generování - změnte počet iterací podle potřeby (3-5 je dobrý start)
    lsystem.generate(4)
    
    # Inicializace okna a kontextu
    window, ctx, width, height = initialize_window()
    
    # Kompilace shaderů
    program = ctx.program(
        vertex_shader=VERTEX_SHADER,
        fragment_shader=FRAGMENT_SHADER
    )
    
    # Získání vertexů stromu
    vertices, colors = lsystem.get_vertices()
    
    # Vytvoření vertex buffer objektu (VBO)
    vbo_vertices = ctx.buffer(vertices.tobytes())
    vbo_colors = ctx.buffer(colors.tobytes())
    
    # Vytvoření vertex array objektu (VAO)
    vao_content = [
        (vbo_vertices, '3f', 'in_position'),
        (vbo_colors, '3f', 'in_color')
    ]
    
    vao = ctx.vertex_array(program, vao_content)
    
    # Nastavení projekční matice (perspektiva)
    projection = Matrix44.perspective_projection(
        45.0, width / height, 0.1, 100.0
    )
    
    # Nastavení pohledové matice
    view = Matrix44.look_at(
        (0, 0, 2),    # pozice kamery
        (0, 0, 0),    # bod, na který kamera míří
        (0, 1, 0)     # up vektor
    )
    
    # Nastavení modelové matice
    model = Matrix44.identity()
    
    # Nastavení uniformů
    program['projection'].write(projection.astype('f4').tobytes())
    program['view'].write(view.astype('f4').tobytes())
    program['model'].write(model.astype('f4').tobytes())
    
    # Nastavení OpenGL
    ctx.enable(moderngl.DEPTH_TEST)
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    
    # Hlavní smyčka
    while not glfw.window_should_close(window):
        # Nastavení barvy pozadí a mazání bufferů
        ctx.clear(0.9, 0.9, 0.9)
        
        # Vykreslení stromu
        vao.render(moderngl.LINES)
        
        # Otáčení modelu pro animaci
        angle = glfw.get_time() * 0.5
        model = Matrix44.from_y_rotation(angle) * Matrix44.from_x_rotation(math.radians(15))
        program['model'].write(model.astype('f4').tobytes())
        
        # Výměna bufferů a zpracování událostí
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    # Úklid
    vbo_vertices.release()
    vbo_colors.release()
    vao.release()
    program.release()
    
    # Ukončení GLFW
    glfw.terminate()


if __name__ == "__main__":
    main()
