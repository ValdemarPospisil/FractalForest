import numpy as np
import moderngl 

class Renderer:
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        vert_src = open('shaders/vertex.glsl').read()
        frag_src = open('shaders/fragment.glsl').read()
        self.prog = self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

        proj = np.array([
            [1.0/(800/600), 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='f4')
        self.prog['projection'].write(proj.tobytes())
        self.color = (0.3, 0.2, 0.1, 1)
        self.buffer = None

    def update_tree(self, tree):
        if self.buffer:
            self.buffer.release()
        data = tree.vertices.tobytes()
        self.buffer = self.ctx.buffer(data)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.buffer, 'in_position')

    def render(self):
        self.ctx.clear(0.5, 0.7, 1.0)
        self.prog['color'].value = self.color
        self.vao.render(mode=moderngl.LINES)

