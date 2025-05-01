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
        self.vao = None

        # Nastavení počátečních OpenGL stavů
        self.ctx.enable(moderngl.DEPTH_TEST)
        # Můžeme zapnout i blendování, pokud budeme mít průhlednost
        # self.ctx.enable(moderngl.BLEND)
        # self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self.ctx.line_width = 2.0 # Mírně tlustší čáry pro lepší viditelnost
        
        logging.info("Renderer initialized successfully")

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
        #glfw.window_hint(glfw.SAMPLES, 4) # Antialiasing (volitelné)

        window = glfw.create_window(self.width, self.height, title, None, None)
        if not window:
            glfw.terminate()
            logging.error("Failed to create GLFW window")
            raise RuntimeError("Nelze vytvořit GLFW okno")

        glfw.make_context_current(window)
        #glfw.swap_interval(1) # VSync (volitelné)
        logging.info(f"GLFW window created with dimensions {self.width}x{self.height}")
        return window

    def setup_object(self, vertices, colors):
        """Vytvoří VBO a VAO pro objekt."""
        # Uvolní staré buffery, pokud existují
        if self.vbo_vertices: self.vbo_vertices.release()
        if self.vbo_colors: self.vbo_colors.release()
        if self.vao: self.vao.release()

        if len(vertices) == 0 or len(colors) == 0:
             logging.warning("No vertices or colors to set up.")
             self.vao = None # Zajistíme, že se nepokusíme vykreslit prázdné VAO
             return

        self.vbo_vertices = self.ctx.buffer(vertices.tobytes())
        self.vbo_colors = self.ctx.buffer(colors.tobytes())

        vao_content = [
            (self.vbo_vertices, '3f', 'in_position'),
            (self.vbo_colors, '3f', 'in_color')
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
