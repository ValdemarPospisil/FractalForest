import moderngl
import glfw
import numpy as np
import logging
import os
from .camera import Camera # Relativní import kamery

class Renderer:
    """Třída pro správu vykreslování pomocí ModernGL."""
    def __init__(self, width=800, height=600, title="L-System Tree Generator"):
        self.width = width
        self.height = height
        self.window = self._initialize_window(title)
        self.ctx = moderngl.create_context()
        
        # Načtení shaderů ze souborů
        self.program = self._load_program('shaders/vertex.glsl', 'shaders/fragment.glsl')

        self.vbo_vertices = None
        self.vbo_colors = None
        self.vbo_normals = None
        self.vao = None

        # Nastavení počátečních OpenGL stavů
        self.ctx.enable(moderngl.DEPTH_TEST)
        # Zapínáme blendování pro hladší vykreslení čar
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Nastavíme maximální možnou tloušťku čar (OpenGL omezuje maximální hodnotu)
        # Zjistíme maximální podporovanou tloušťku čar na aktuálním hardware
        max_line_width = self.ctx.info['GL_ALIASED_LINE_WIDTH_RANGE'][1]
        logging.info(f"Maximum supported line width: {max_line_width}")
        self.ctx.line_width = min(10.0, max_line_width)  # Použijeme menší z hodnot 10.0 nebo max podporované
        self.program['light_direction'] = (0.5, 1.0, 0.5)
        
        logging.info(f"Renderer initialized successfully with line width: {self.ctx.line_width}")

    def _load_program(self, vertex_path, fragment_path):
        """Načte a zkompiluje shader program ze souborů."""
        try:
            with open(vertex_path, 'r') as f:
                vertex_shader = f.read()
            
            with open(fragment_path, 'r') as f:
                fragment_shader = f.read()
                
            return self.ctx.program(
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader
            )
        except Exception as e:
            logging.error(f"Failed to load shaders: {e}")
            raise

    def _initialize_window(self, title):
        """Inicializuje GLFW okno."""
        if not glfw.init():
            logging.error("Failed to initialize GLFW")
            raise RuntimeError("Nelze inicializovat GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.SAMPLES, 4) # Zapneme antialiasing pro hladší čáry

        window = glfw.create_window(self.width, self.height, title, None, None)
        if not window:
            glfw.terminate()
            logging.error("Failed to create GLFW window")
            raise RuntimeError("Nelze vytvořit GLFW okno")

        glfw.make_context_current(window)
        glfw.swap_interval(1) # Zapneme VSync pro plynulejší zobrazení
        logging.info(f"GLFW window created with dimensions {self.width}x{self.height}")
        return window

    # Upravená metoda setup_object - může vytvářet tlustší linie pomocí duplikovaných vrcholů
    def setup_object(self, vertices, colors, normals=None):
        """Vytvoří VBO a VAO pro objekt."""
        # Uvolní staré buffery, pokud existují
        if self.vbo_vertices: self.vbo_vertices.release()
        if self.vbo_colors: self.vbo_colors.release()
        if self.vbo_normals: self.vbo_normals.release()
        if self.vao: self.vao.release()

        if len(vertices) == 0 or len(colors) == 0:
            logging.warning("No vertices or colors to set up.")
            self.vao = None
            return

        self.vbo_vertices = self.ctx.buffer(vertices.tobytes())
        self.vbo_colors = self.ctx.buffer(colors.tobytes())
    
        # Pokud normály nejsou poskytnuty, vytvoříme základní
        if normals is None:
            # Vytvoříme jednoduché normály (v reálném stromu by byly sofistikovanější)
            normals = np.zeros_like(vertices)
            for i in range(0, len(vertices), 6):  # Pro každý pár vrcholů (čáru)
                if i+3 < len(vertices):
                    # Vytvoříme normálu kolmou k segmentu
                    direction = vertices[i+3:i+6] - vertices[i:i+3]
                    # Rotujeme o 90 stupňů kolem osy Y pro základní normálu
                    normal = np.array([direction[2], 0, -direction[0]])
                    if np.linalg.norm(normal) < 0.001:
                        normal = np.array([0, 1, 0])  # Fallback
                    else:
                        normal = normal / np.linalg.norm(normal)
                
                    normals[i:i+3] = normal
                    normals[i+3:i+6] = normal
    
        self.vbo_normals = self.ctx.buffer(normals.astype('f4').tobytes())

        vao_content = [
            (self.vbo_vertices, '3f', 'in_position'),
            (self.vbo_colors, '3f', 'in_color'),
            (self.vbo_normals, '3f', 'in_normal')
        ]
        self.vao = self.ctx.vertex_array(self.program, vao_content)
        logging.debug(f"Object set up with {len(vertices)//3} vertices")

    def render(self, camera: Camera, model_matrix):
        """Vykreslí scénu."""
        self.ctx.clear(0.9, 0.95, 1.0) # Světle modrá obloha

        if not self.vao:
            return # Nic k vykreslení

        # Aktualizace uniformů
        self.program['projection'].write(camera.get_projection_matrix_bytes())
        self.program['view'].write(camera.get_view_matrix_bytes())
        self.program['model'].write(model_matrix.astype('f4').tobytes())

        # Vykreslení
        self.vao.render(moderngl.LINES) # Vykreslujeme čáry

    def cleanup(self):
        """Uvolní OpenGL zdroje."""
        if self.vbo_vertices: self.vbo_vertices.release()
        if self.vbo_colors: self.vbo_colors.release()
        if self.vbo_normals: self.vbo_normals.release()
        if self.vao: self.vao.release()
        if self.program: self.program.release()
        logging.info("OpenGL resources released")
        # Kontext se uvolní automaticky při ukončení programu,
        # ale explicitní uvolnění není na škodu, pokud by se renderer používal déle.
        # self.ctx.release()

    def should_close(self):
        """Zkontroluje, zda má být okno zavřeno."""
        return glfw.window_should_close(self.window)

    def swap_buffers(self):
        """Vymění buffery okna."""
        glfw.swap_buffers(self.window)

    def poll_events(self):
        """Zpracuje události okna."""
        glfw.poll_events()
