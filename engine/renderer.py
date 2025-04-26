"""
Základní renderovací systém
"""
import os
import logging
import moderngl
import numpy as np
from engine.shader import ShaderProgram

logger = logging.getLogger('FractalForest.Renderer')

class Renderer:
    """Třída pro správu renderování scény"""
    
    def __init__(self, ctx, camera):
        logger.info("Initializing Renderer")
        self.ctx = ctx
        self.camera = camera
        
        # Načtení základních shaderů
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shaders')
        logger.debug(f"Loading shaders from directory: {shader_dir}")
        
        vertex_path = os.path.join(shader_dir, 'basic.vert')
        fragment_path = os.path.join(shader_dir, 'basic.frag')
        
        # Check if shader files exist
        if not os.path.exists(vertex_path):
            logger.error(f"Vertex shader not found: {vertex_path}")
        if not os.path.exists(fragment_path):
            logger.error(f"Fragment shader not found: {fragment_path}")
            
        try:
            self.basic_shader = ShaderProgram(
                self.ctx,
                vertex_path,
                fragment_path
            )
            logger.info("Basic shader compiled successfully")
        except Exception as e:
            logger.error(f"Failed to compile shaders: {e}")
            raise
        
        # Nastavení základního barevného modelu
        try:
            self.basic_shader.use()
            self.basic_shader.set_uniform('light_position', [100.0, 100.0, 100.0])
            self.basic_shader.set_uniform('light_color', [1.0, 1.0, 1.0])
            self.basic_shader.set_uniform('ambient_strength', 0.3)
            logger.debug("Basic shader uniforms set")
        except Exception as e:
            logger.error(f"Failed to set shader uniforms: {e}")
            raise
        
    def render(self, forest):
        """Vykreslí celou scénu"""
        if forest is None:
            logger.warning("Attempted to render None forest")
            return
            
        if len(forest.trees) == 0:
            logger.warning("Forest has no trees to render")
            return
            
        # Debug first check if trees have VAOs
        valid_trees = sum(1 for tree in forest.trees if hasattr(tree, 'vao') and tree.vao is not None)
        logger.debug(f"Rendering forest with {valid_trees}/{len(forest.trees)} valid trees")
            
        # Nastavení pohledové a projekční matice
        try:
            self.basic_shader.use()
            self.basic_shader.set_uniform('view', self.camera.view_matrix)
            self.basic_shader.set_uniform('projection', self.camera.projection_matrix)
        except Exception as e:
            logger.error(f"Failed to set view/projection matrices: {e}")
            return
        
        # Vykreslení všech stromů v lese
        trees_rendered = 0
        for i, tree in enumerate(forest.trees):
            try:
                self.render_tree(tree)
                trees_rendered += 1
            except Exception as e:
                logger.error(f"Failed to render tree {i}: {e}")
                
        logger.debug(f"Trees rendered: {trees_rendered}/{len(forest.trees)}")
            
    def render_tree(self, tree):
        """Vykreslí jeden strom"""
        if tree.geometry is None:
            logger.debug(f"Tree {id(tree)} has no geometry")
            return
            
        if not hasattr(tree, 'vao') or tree.vao is None:
            logger.debug(f"Tree {id(tree)} has no VAO")
            return
            
        # Nastavení modelové matice pro strom
        try:
            model_matrix = tree.get_model_matrix()
            self.basic_shader.set_uniform('model', model_matrix)
            
            # Nastavení barvy stromu
            self.basic_shader.set_uniform('object_color', tree.color)
        except Exception as e:
            logger.error(f"Error setting tree uniforms: {e}")
            return
        
        # Vykreslení stromu
        try:
            tree.vao.render()
        except Exception as e:
            logger.error(f"Error rendering tree VAO: {e}")
            
    def create_tree_vao(self, tree):
        """Vytvoří VAO pro strom na základě jeho geometrie"""
        if tree.geometry is None:
            logger.warning(f"Cannot create VAO for tree {id(tree)}: no geometry")
            return
            
        # Získání dat geometrie
        vertices, normals, indices = tree.geometry
        
        # Kontrola, zda geometrie obsahuje platná data
        if len(vertices) == 0 or len(normals) == 0 or len(indices) == 0:
            logger.warning(f"Empty geometry for tree type {tree.tree_type}")
            return
            
        logger.debug(f"Creating VAO for {tree.tree_type} tree with {len(vertices)} vertices and {len(indices)} indices")
            
        try:
            # Vytvoření vertex bufferu
            vertex_buffer = self.ctx.buffer(vertices.astype('f4').tobytes())
            normal_buffer = self.ctx.buffer(normals.astype('f4').tobytes())
            index_buffer = self.ctx.buffer(indices.astype('i4').tobytes())
            
            # Debugging buffer sizes
            logger.debug(f"Buffer sizes: vertices={len(vertices)*4*3}B, normals={len(normals)*4*3}B, indices={len(indices)*4}B")
            
            # Vytvoření VAO
            tree.vao = self.ctx.vertex_array(
                self.basic_shader.program,
                [
                    (vertex_buffer, '3f', 'position'),
                    (normal_buffer, '3f', 'normal')
                ],
                index_buffer
            )
            logger.debug(f"Successfully created VAO for tree {id(tree)}")
        except Exception as e:
            logger.error(f"Failed to create VAO: {e}")
            logger.error(f"Vertex data shape: {vertices.shape}, Normal data shape: {normals.shape}, Index data shape: {indices.shape}")
