import pyglet
import moderngl 
import numpy as np
import logging
from generation.lsystem import LSystem
from generation.tree import Tree
from engine.renderer import Renderer
from ui.gui import GUI


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fractalforest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FractalForest')

class FractalForestApp(pyglet.window.Window):
    def __init__(self):
        super().__init__(1280, 720, "FractalForest")
        self.ctx = moderngl.create_context()
        self.renderer = Renderer(self.ctx)
        self.gui = GUI(self)
        self.generate_tree()

        self.setup_events()

    def generate_tree(self):
        ls = LSystem.create_tree_system(tree_type="oak", randomness=0.4)
        instr = ls.generate(5)
        self.tree = Tree(instr)
        self.renderer.update_tree(self.tree)

    def on_draw(self):
        self.clear()
        self.renderer.render()
        self.gui.draw()

    def setup_events(self):
        """Nastavení event handlerů pro pyglet"""
        logger.debug("Setting up event handlers")
        
        @self.event
        def on_key_press(symbol, modifiers):
            # Debug key presses
            key_name = pyglet.window.key.symbol_string(symbol)
            logger.debug(f"Key pressed: {key_name}")
                    
            # Generování nového lesa
            if symbol == pyglet.window.key.G:
                logger.info("Regenerating forest")
                self.generate_tree()
                
            # Ukončení aplikace
            elif symbol == pyglet.window.key.ESCAPE:
                logger.info("Application exit requested")
                pyglet.app.exit()

if __name__ == "__main__":
    app = FractalForestApp()
    pyglet.app.run()
