import numpy as np
import moderngl

class Renderer:
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx

        vert_src = open('shaders/basic.vert').read()
        frag_src = open('shaders/basic.frag').read()
        self.prog = self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

        # Nastavení projekční matice (pravděpodobně perspektivní nebo ortografická)
        aspect_ratio = 800 / 600
        proj = np.array([
            [1.0/aspect_ratio, 0.0, 0.0, 0.0],
            [0.0, 1.0,         0.0, 0.0],
            [0.0, 0.0,         1.0, 0.0],
            [0.0, 0.0,         0.0, 1.0]
        ], dtype='f4')
        self.prog['projection'].write(proj.tobytes())

        self.color = (0.3, 0.2, 0.1, 1.0)
        self.buffer = None

    def update_tree(self, tree):
        if self.buffer:
            self.buffer.release()

        # tree.vertices musí obsahovat [position.x, position.y, position.z, normal.x, normal.y, normal.z]
        data = tree.vertices.tobytes()
        self.buffer = self.ctx.buffer(data)

        # Vytvoření VAO - musíme připojit i normály
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.buffer, '3f 3f', 'position', 'normal')
            ]
        )

    def render(self):
        self.ctx.clear(0.5, 0.7, 1.0)

        # Nastavit model a view matici
        model = np.eye(4, dtype='f4')  # jednoduchá jednotková matice
        view = np.eye(4, dtype='f4')   # taky zatím jednoduchá (např. kamera v 0,0,0)

        # Normal matrix
        normal_matrix = np.linalg.inv(model[:3, :3]).T  # Inverzní + transpozice

        # Zapsat do shaderu
        self.prog['model'].write(model.tobytes())
        self.prog['view'].write(view.tobytes())

        # Poslat světlo a barvu (pokud máš uniformy light_position, light_color, ambient_strength)
        self.prog['light_position'].value = (10.0, 10.0, 10.0)
        self.prog['light_color'].value = (1.0, 1.0, 1.0)
        self.prog['ambient_strength'].value = 0.2
        self.prog['object_color'].value = (0.3, 0.5, 0.2)  # zelená pro stromy

        self.vao.render(mode=moderngl.LINES)  # asi budeš chtít TRIANGLES, ne LINES
