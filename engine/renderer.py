import numpy as np
import moderngl

class Renderer:
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx

        vert_src = open('shaders/basic.vert').read()
        frag_src = open('shaders/basic.frag').read()
        self.prog = self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

        # Set up projection matrix (orthographic or perspective)
        aspect_ratio = 800 / 600
        fov = 45.0  # Field of view in degrees
        near = 0.1
        far = 100.0
        
        # Create perspective projection matrix
        self.proj = self.perspective_matrix(fov, aspect_ratio, near, far)
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
        # Create a large flat plane (10x10 units)
        vertices = np.array([
            # Position         # Normal (up)
            -5, 0, -5,        0, 1, 0,  # Bottom-left
            -5, 0,  5,        0, 1, 0,  # Top-left
             5, 0,  5,        0, 1, 0,  # Top-right
             5, 0, -5,        0, 1, 0,  # Bottom-right
        ], dtype='f4')
        
        indices = np.array([
            0, 1, 2,
            0, 2, 3
        ], dtype='i4')
        
        vert_src = open('shaders/basic.vert').read()
        frag_src = open('shaders/basic.frag').read()
             
        self.ground_vao = self.ctx.vertex_array(
            self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src),  # Use same shader as your tree or create a simple one
            [
                (self.ctx.buffer(vertices), '3f 3f', 'position', 'normal'),
            ],
            index_buffer=self.ctx.buffer(indices)
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

    def render(self, camera_pos, view_matrix):

        self._render_ground(view_matrix)

        # Clear the framebuffer
        self.ctx.clear(0.5, 0.7, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        # Simple model matrix (identity for now)
        model = np.eye(4, dtype='f4')

        # Set uniforms for model and view matrices
        self.prog['model'].write(model.tobytes())
        self.prog['view'].write(view_matrix.tobytes())

        # Set lighting parameters
        self.prog['light_position'].value = (10.0, 10.0, 10.0)
        self.prog['light_color'].value = (1.0, 1.0, 1.0)
        self.prog['ambient_strength'].value = 0.3
        self.prog['object_color'].value = self.color

        # Render the tree as triangles
        if self.vao:
            self.vao.render(mode=moderngl.TRIANGLES)


    def _render_ground(self, view_matrix):
        # Simple ground shader with grid pattern
        ground_color = (0.3, 0.3, 0.3)  # Dark gray
        grid_color = (0.5, 0.5, 0.5)    # Light gray
        
        # Set uniforms and render
        self.ground_vao.program['view'].write(vier()
