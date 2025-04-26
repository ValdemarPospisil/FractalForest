"""
Základní renderovací systém
"""
import os
import moderngl
import numpy as np
from engine.shader import ShaderProgram

class Renderer:
    """Třída pro správu renderování scény"""
    
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.camera = camera
        
        # Načtení základních shaderů
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shaders')
        self.basic_shader = ShaderProgram(
            self.ctx,
            os.path.join(shader_dir, 'basic.vert'),
            os.path.join(shader_dir, 'basic.frag')
        )
        
        # Nastavení základního barevného modelu
        self.basic_shader.use()
        self.basic_shader.set_uniform('light_position', [100.0, 100.0, 100.0])
        self.basic_shader.set_uniform('light_color', [1.0, 1.0, 1.0])
        self.basic_shader.set_uniform('ambient_strength', 0.3)
        
    def render(self, forest):
        """Vykreslí celou scénu"""
        if forest is None:
            return
            
        # Nastavení pohledové a projekční matice
        self.basic_shader.use()
        self.basic_shader.set_uniform('view', self.camera.view_matrix)
        self.basic_shader.set_uniform('projection', self.camera.projection_matrix)
        
        # Vykreslení všech stromů v lese
        for tree in forest.trees:
            self.render_tree(tree)
            
    def render_tree(self, tree):
        """Vykreslí jeden strom"""
        if tree.geometry is None or not hasattr(tree, 'vao'):
            return
            
        # Nastavení modelové matice pro strom
        self.basic_shader.set_uniform('model', tree.get_model_matrix())
        
        # Nastavení barvy stromu
        self.basic_shader.set_uniform('object_color', tree.color)
        
        # Vykreslení stromu
        tree.vao.render()
        
    def create_tree_vao(self, tree):
        """Vytvoří VAO pro strom na základě jeho geometrie"""
        if tree.geometry is None:
            return
            
        # Získání dat geometrie
        vertices, normals, indices = tree.geometry
        
        # Kontrola, zda geometrie obsahuje platná data
        if len(vertices) == 0 or len(normals) == 0 or len(indices) == 0:
            print(f"Prázdná geometrie pro strom typu {tree.tree_type}")
            return
            
        try:
            # Vytvoření vertex bufferu
            vertex_buffer = self.ctx.buffer(vertices.astype('f4').tobytes())
            normal_buffer = self.ctx.buffer(normals.astype('f4').tobytes())
            index_buffer = self.ctx.buffer(indices.astype('i4').tobytes())
            
            # Vytvoření VAO
            tree.vao = self.ctx.vertex_array(
                self.basic_shader.program,
                [
                    (vertex_buffer, '3f', 'position'),
                    (normal_buffer, '3f', 'normal')
                ],
                index_buffer
            )
        except Exception as e:
            print(f"Chyba při vytváření VAO: {e}")
