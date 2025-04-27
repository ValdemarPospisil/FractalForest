import numpy as np
import moderngl

class Renderer:
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx

        vert_src = open('shaders/basic.vert').read()
        frag_src = open('shaders/basic.frag').read()
        self.prog = self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

        # Set up projection matrix with wider viewing frustum
        self.aspect_ratio = 1280 / 720
        self.fov = 75.0  # Field of view in degrees
        self.near = 0.1
        self.far = 500.0  # Increased far plane distance
        
        # Create perspective projection matrix
        self.proj = self.perspective_matrix(self.fov, self.aspect_ratio, self.near, self.far)
        self.prog['projection'].write(self.proj.tobytes())

        self.color = (0.3, 0.2, 0.1, 1.0)
        self.vbo = None
        self.ibo = None
        self.vao = None
        self._init_ground_plane()

    def perspective_matrix(self, fov, aspect, near, far):
        """Create a perspective projection matrix"""
        fov_rad = np.radians(fov)
        f = 1.0 / np.tan(fov_rad / 2.0)
        
        return np.array([
            [f / aspect, 0.0, 0.0, 0.0],
            [0.0, f, 0.0, 0.0],
            [0.0, 0.0, (far + near) / (near - far), -1.0],
            [0.0, 0.0, (2.0 * far * near) / (near - far), 0.0]
        ], dtype='f4')

    def _init_ground_plane(self):
        # Create a much larger flat plane (50x50 units instead of 10x10)
        size = 50.0
        vertices = np.array([
            # Position         # Normal (up)
            -size, 0, -size,   0, 1, 0,  # Bottom-left
            -size, 0,  size,   0, 1, 0,  # Top-left
             size, 0,  size,   0, 1, 0,  # Top-right
             size, 0, -size,   0, 1, 0,  # Bottom-right
        ], dtype='f4')
        
        indices = np.array([
            0, 1, 2,
            0, 2, 3
        ], dtype='i4')
        
        # Use the same shader program for ground
        self.ground_prog = self.ctx.program(
            vertex_shader=open('shaders/basic.vert').read(),
            fragment_shader=open('shaders/basic.frag').read()
        )
             
        # Create ground vertex array
        self.ground_vbo = self.ctx.buffer(vertices)
        self.ground_ibo = self.ctx.buffer(indices)
        
        self.ground_vao = self.ctx.vertex_array(
            self.ground_prog,
            [
                (self.ground_vbo, '3f 3f', 'position', 'normal'),
            ],
            self.ground_ibo
        )

    def update_tree(self, tree):
        # Release previous buffers if they exist
        if self.vbo:
            self.vbo.release()
        if self.ibo:
            self.ibo.release()
        if self.vao:
            self.vao.release()

        # Get vertex data and indices from the tree
        vertices = tree.vertices
        indices = tree.indices

        # Create vertex buffer
        self.vbo = self.ctx.buffer(vertices.tobytes())
        
        # Create index buffer
        self.ibo = self.ctx.buffer(indices.tobytes())

        # Create vertex array object with both position and normal attributes
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.vbo, '3f 3f', 'position', 'normal')],
            self.ibo
        )

    def render(self, view_matrix):
        # Clear the framebuffer
        self.ctx.clear(0.5, 0.7, 1.0, depth=1.0)
        # Enable depth testing and face culling
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        # Simple model matrix (identity for now)
        model = np.eye(4, dtype='f4')

        # First render the ground
        self._render_ground(model, view_matrix)
        
        # Then render the tree
        self._render_tree(model, view_matrix)

    def _render_ground(self, model, view_matrix):
        # Set uniforms for ground plane
        self.ground_prog['model'].write(model.tobytes())
        self.ground_prog['view'].write(view_matrix.tobytes())
        self.ground_prog['projection'].write(self.proj.tobytes())
        
        # Set lighting parameters
        self.ground_prog['light_position'].value = (10.0, 10.0, 10.0)
        self.ground_prog['light_color'].value = (1.0, 1.0, 1.0)
        self.ground_prog['ambient_strength'].value = 0.3
        self.ground_prog['object_color'].value = (0.3, 0.2, 0.1, 1.0)  # Gray color for ground
        self.ground_prog['is_ground'].value = True  # Flag for ground shader effects
        
        # Render the ground plane
        self.ground_vao.render(mode=moderngl.TRIANGLES)
        
    def _render_tree(self, model, view_matrix):
        # Set uniforms for tree
        self.prog['model'].write(model.tobytes())
        self.prog['view'].write(view_matrix.tobytes())
        self.prog['projection'].write(self.proj.tobytes())

        # Set lighting parameters
        self.prog['light_position'].value = (10.0, 10.0, 10.0)
        self.prog['light_color'].value = (1.0, 1.0, 1.0)
        self.prog['ambient_strength'].value = 0.3
        self.prog['object_color'].value = (0.3, 0.75, 0.1, 1.0)
        self.prog['is_ground'].value = False  # Not ground
        
        # Render the tree as triangles
        if self.vao:
            self.vao.render(mode=moderngl.TRIANGLES)
    
    def update_projection(self, width, height):
        """Update projection matrix based on new window dimensions"""
        self.aspect_ratio = width / height
        self.proj = self.perspective_matrix(self.fov, self.aspect_ratio, self.near, self.far)
        self.prog['projection'].write(self.proj.tobytes())
        self.ground_prog['projection'].write(self.proj.tobytes())
