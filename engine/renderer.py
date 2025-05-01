import moderngl
import numpy as np
import logging
import os

# Nastavení loggeru
logger = logging.getLogger('FractalForest.Renderer')

class Renderer:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.camera = camera
        
        logger.info("Inicializace rendereru")
        
        # Vertex a fragment shadery
        self.shader_program = self._create_shader_program()
        
        # Vytvoření prázdného VAO a VBO
        self.vao = None
        self.vbo = None
        self.ibo = None
        self.vertex_count = 0
        
    def _create_shader_program(self):
        """Vytvoření shader programu pro vykreslování stromů"""
        logger.info("Vytváření shader programu")
        
        # Načtení shaderů ze souborů
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shaders')
        
        try:
            # Zajištění, že adresář pro shadery existuje
            os.makedirs(shader_dir, exist_ok=True)
            
            # Cesty k souborům shaderů
            vertex_shader_path = os.path.join(shader_dir, 'vertex.glsl')
            fragment_shader_path = os.path.join(shader_dir, 'fragment.glsl')
            
            # Načtení obsahu shaderů
            with open(vertex_shader_path, 'r') as f:
                vertex_shader = f.read()
                
            with open(fragment_shader_path, 'r') as f:
                fragment_shader = f.read()
            
            program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
            logger.info("Shader program úspěšně vytvořen")
            return program
        except Exception as e:
            logger.error(f"Chyba při vytváření shader programu: {e}")
            logger.info("Použití záložního shader programu")
        try:
            program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
            logger.info("Záložní shader program úspěšně vytvořen")
            return program
        except Exception as e:
            logger.error(f"Kritická chyba při vytváření záložního shader programu: {e}")
            raise
    
    def update_geometry(self, vertices, indices):
        """Aktualizuje geometrii stromu"""
        logger.info(f"Aktualizace geometrie: {len(vertices)/7} vrcholů, {len(indices)} indexů")
        
        # Kontrola dat před vytvořením bufferů
        if len(vertices) == 0 or len(indices) == 0:
            logger.warning("Prázdná geometrie - žádné vrcholy nebo indexy")
            return
            
        try:
            # Logování struktury vertexů pro debugování
            if isinstance(vertices, np.ndarray):
                logger.debug(f"Tvar vertex pole: {vertices.shape}")
            else:
                logger.debug(f"Typ vertices není numpy array: {type(vertices)}")
                vertices = np.array(vertices, dtype=np.float32)
                
            vertex_size = 7  # 3 pozice + 4 barva
            if len(vertices) % vertex_size != 0:
                logger.error(f"Nesprávný formát vertexů: {len(vertices)} hodnot není dělitelných {vertex_size}")
                
            # Vyčištění předchozích bufferů, pokud existují
            if self.vbo:
                self.vbo.release()
            if self.ibo:
                self.ibo.release()
            if self.vao:
                self.vao.release()
            
            # Vytvoření nových bufferů
            self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
            self.ibo = self.ctx.buffer(indices.astype('u4').tobytes())
            
            # Vytvoření VAO
            self.vao = self.ctx.vertex_array(
                self.shader_program,
                [
                    (self.vbo, '3f 4f', 'in_position', 'in_color')
                ],
                self.ibo
            )
            
            # Nastavení počtu vrcholů
            self.vertex_count = len(indices)
            logger.info(f"Geometrie úspěšně aktualizována, počet indexů: {self.vertex_count}")
            
        except Exception as e:
            logger.error(f"Chyba při aktualizaci geometrie: {e}")
            logger.debug(f"První 5 vrcholů: {vertices[:35] if len(vertices) >= 35 else vertices}")
            raise
    
    def render(self):
        """Vykreslí strom"""
        if not self.vao or self.vertex_count == 0:
            return
        
        try:
            # Nastavení uniformních proměnných pro shadery
            # Oprava: Zajištění správného formátu matic pomocí flatten()
            model_matrix = np.identity(4, dtype=np.float32).flatten()
            view_matrix = self.camera.get_view_matrix().astype(np.float32).flatten()
            projection_matrix = self.camera.get_projection_matrix().astype(np.float32).flatten()
            
            # Nastavení uniformních proměnných
            self.shader_program['model'].write(model_matrix)
            self.shader_program['view'].write(view_matrix)
            self.shader_program['projection'].write(projection_matrix)
            
            # Vykreslení stromu
            self.vao.render(moderngl.TRIANGLES)
        except Exception as e:
            logger.error(f"Chyba při vykreslování: {e}")
            # Více informací o chybě
            logger.debug(f"Model matrix typ: {type(model_matrix)}, tvar: {model_matrix.shape}")
            logger.debug(f"View matrix typ: {type(view_matrix)}, tvar: {view_matrix.shape}")
            logger.debug(f"Projection matrix typ: {type(projection_matrix)}, tvar: {projection_matrix.shape}")
    
    def cleanup(self):
        """Uvolnění OpenGL zdrojů"""
        logger.info("Úklid OpenGL zdrojů")
        if self.vbo:
            self.vbo.release()
        if self.ibo:
            self.ibo.release()
        if self.vao:
            self.vao.release()
        if self.shader_program:
            self.shader_program.release()
