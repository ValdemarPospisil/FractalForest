#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import moderngl
import numpy as np

class Renderer:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.camera = camera
        
        # Vertex a fragment shadery
        self.shader_program = self._create_shader_program()
        
        # Vytvoření prázdného VAO a VBO
        self.vao = None
        self.vbo = None
        self.ibo = None
        self.vertex_count = 0
        
    def _create_shader_program(self):
        """Vytvoření shader programu pro vykreslování stromů"""
        vertex_shader = '''
            #version 330 core
            
            layout(location = 0) in vec3 in_position;
            layout(location = 1) in vec4 in_color;
            
            out vec4 v_color;
            
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            
            void main() {
                v_color = in_color;
                gl_Position = projection * view * model * vec4(in_position, 1.0);
            }
        '''
        
        fragment_shader = '''
            #version 330 core
            
            in vec4 v_color;
            out vec4 f_color;
            
            void main() {
                f_color = v_color;
            }
        '''
        
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    
    def update_geometry(self, vertices, indices):
        """Aktualizuje geometrii stromu"""
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
    
    def render(self):
        """Vykreslí strom"""
        if not self.vao or self.vertex_count == 0:
            return
        
        # Nastavení uniformních proměnných pro shadery
        self.shader_program['model'] = np.identity(4, dtype=np.float32)
        self.shader_program['view'] = self.camera.get_view_matrix()
        self.shader_program['projection'] = self.camera.get_projection_matrix()
        
        # Vykreslení stromu
        self.vao.render(moderngl.TRIANGLES)
    
    def cleanup(self):
        """Uvolnění OpenGL zdrojů"""
        if self.vbo:
            self.vbo.release()
        if self.ibo:
            self.ibo.release()
        if self.vao:
            self.vao.release()
        if self.shader_program:
            self.shader_program.release()
