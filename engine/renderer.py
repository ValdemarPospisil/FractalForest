import moderngl
import glfw
import numpy as np
import logging
from .camera import Camera

class Renderer:
    """Třída pro správu vykreslování pomocí ModernGL."""
    def __init__(self, width=800, height=600, title="L-System Tree Generator"):
        self.width = width
        self.height = height
        self.window = self._initialize_window(title)
        self.ctx = moderngl.create_context()
        
        # Načtení shaderů ze souborů
        self.program = self._load_program('shaders/vertex.glsl', 'shaders/fragment.glsl')

        # Inicializace pro více objektů
        self.objects = {}

        # Nastavení počátečních OpenGL stavů
        self.ctx.enable(moderngl.DEPTH_TEST)
        # Můžeme zapnout i blendování, pokud budeme mít průhlednost
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self.ctx.line_width = 150 # Mírně tlustší čáry pro lepší viditelnost
        self.program['light_direction'] = (0.5, 1.0, 0.5)
        
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
        glfw.window_hint(glfw.SAMPLES, 4) # Antialiasing (volitelné)

        window = glfw.create_window(self.width, self.height, title, None, None)
        if not window:
            glfw.terminate()
            logging.error("Failed to create GLFW window")
            raise RuntimeError("Nelze vytvořit GLFW okno")

        glfw.make_context_current(window)
        glfw.swap_interval(1) # VSync (volitelné)
        logging.info(f"GLFW window created with dimensions {self.width}x{self.height}")
        return window

    def setup_object(self, vertices, colors, normals=None, object_id="tree", primitive=moderngl.LINES):
        """Vytvoří VBO a VAO pro objekt s daným ID."""
        # Uvolní staré buffery daného objektu, pokud existují
        if object_id in self.objects:
            obj = self.objects[object_id]
            if 'vbo_vertices' in obj: obj['vbo_vertices'].release()
            if 'vbo_colors' in obj: obj['vbo_colors'].release()
            if 'vbo_normals' in obj: obj['vbo_normals'].release()
            if 'vao' in obj: obj['vao'].release()

        if len(vertices) == 0 or len(colors) == 0:
            #logging.warning(f"No vertices or colors to set up for object {object_id}.")
            if object_id in self.objects:
                del self.objects[object_id]
            return

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

        vbo_vertices = self.ctx.buffer(vertices.tobytes())
        vbo_colors = self.ctx.buffer(colors.tobytes())
        vbo_normals = self.ctx.buffer(normals.astype('f4').tobytes())

        vao_content = [
            (vbo_vertices, '3f', 'in_position'),
            (vbo_colors, '3f', 'in_color'),
            (vbo_normals, '3f', 'in_normal')
        ]
        vao = self.ctx.vertex_array(self.program, vao_content)

        # Uložíme objekt do slovníku
        self.objects[object_id] = {
            'vbo_vertices': vbo_vertices,
            'vbo_colors': vbo_colors,
            'vbo_normals': vbo_normals,
            'vao': vao,
            'primitive': primitive
        }
        
        logging.debug(f"Object {object_id} set up with {len(vertices)//3} vertices")

    def create_ground(self, size=20.0, color=(0.6, 0.4, 0.2)):
        """Vytvoří širokou plochou zem."""
        # Vytvoříme jednoduchý čtverec jako zem
        half_size = size / 2
        vertices = np.array([
            -half_size, 0.0, -half_size,
            half_size, 0.0, -half_size,
            half_size, 0.0, half_size,
            
            half_size, 0.0, half_size,
            -half_size, 0.0, half_size,
            -half_size, 0.0, -half_size
        ], dtype='f4')
        
        # Barva pro všechny vrcholy
        colors = np.array([color] * 6, dtype='f4')
        
        # Normály směřující vzhůru
        normals = np.array([(0.0, 1.0, 0.0)] * 6, dtype='f4')
        
        # Nastavíme zem jako samostatný objekt
        self.setup_object(vertices, colors, normals, object_id="ground", primitive=moderngl.TRIANGLES)
        logging.info(f"Ground plane created with size {size}x{size}")

    def render(self, camera: Camera, model_matrix):
        """Vykreslí scénu."""
        self.ctx.clear(0.9, 0.95, 1.0) # Světle modrá obloha

        if not self.objects:
            return # Nic k vykreslení

        # Aktualizace uniformů
        self.program['projection'].write(camera.get_projection_matrix_bytes())
        self.program['view'].write(camera.get_view_matrix_bytes())
        self.program['model'].write(model_matrix.astype('f4').tobytes())

        # Vykreslení všech objektů
        for obj_id, obj in self.objects.items():
            if 'vao' in obj:
                obj['vao'].render(obj['primitive'])

    def cleanup(self):
        """Uvolní OpenGL zdroje."""
        # Uvolníme všechny objekty
        for obj_id, obj in self.objects.items():
            if 'vbo_vertices' in obj: obj['vbo_vertices'].release()
            if 'vbo_colors' in obj: obj['vbo_colors'].release()
            if 'vbo_normals' in obj: obj['vbo_normals'].release()
            if 'vao' in obj: obj['vao'].release()
        
        self.objects = {}
        
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
