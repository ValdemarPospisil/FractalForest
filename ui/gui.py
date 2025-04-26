import pyglet

class GUI:
    def __init__(self, window):
        self.label = pyglet.text.Label(
            "Press G to generate a new tree",
            x=10, y=10,
            color=(0, 0, 0, 255)
        )
    def draw(self):
        self.label.draw()
