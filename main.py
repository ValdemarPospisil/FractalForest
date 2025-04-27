import pyglet
import moderngl
import random
import logging
import numpy as np
from pyglet.window import key
from generation.lsystem import LSystem
from generation.tree import Tree
from engine.renderer import Renderer
from engine.camera import Camera
from ui.gui import GUI


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fractalforest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Available tree types
TREE_TYPES = ["pine", "oak", "bush"]

class FractalForestApp(pyglet.window.Window):
    def __init__(self, width=1280, height=720):
        super().__init__(width, height, "FractalForest")
        self.ctx = moderngl.create_context()
        self.renderer = Renderer(self.ctx)
        self.camera = Camera(self)
        self.gui = GUI(self)
        
        # Set up update schedule
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        
        self.generate_random_tree()
    
    def generate_tree(self):
        ls = LSystem.create_tree_system(tree_type="oak", randomness=0.4)
        instr = ls.generate(5)
        self.tree = Tree(instr)
        self.renderer.update_tree(self.tree)
    
    def generate_random_tree(self):
        """Generate a random tree from available types"""
        tree_type = random.choice(TREE_TYPES)
        logger.info(f"Generating new tree of type: {tree_type}")
        
        # Set specific parameters based on tree type
        if tree_type == "pine":
            iterations = 4
            angle = 22.5
            length = 0.08
            color = (0.1, 0.4, 0.1, 1.0)  # Dark green
        elif tree_type == "oak":
            iterations = 4
            angle = 25.0
            length = 0.06
            color = (0.3, 0.5, 0.2, 1.0)  # Medium green
        elif tree_type == "bush":
            iterations = 3
            angle = 28.0
            length = 0.09
            color = (0.4, 0.6, 0.3, 1.0)  # Light green
            
        # Generate L-system and tree
        lsystem = LSystem.create_tree_system(tree_type=tree_type, randomness=0.15)
        instructions = lsystem.generate(iterations)
        self.tree = Tree(instructions, angle=angle, length=length, tree_type=tree_type)
        
        # Update renderer with tree and color
        self.renderer.update_tree(self.tree)
        self.renderer.color = color
        
        # Update GUI with tree type info
        self.gui.update_tree_info(tree_type)

    def update(self, dt):
        """Update function called by pyglet clock"""
        # Process keyboard input for camera movement
        self.camera.process_keyboard(dt)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.G:
            self.generate_random_tree()
        elif symbol == key.ESCAPE:
            pyglet.app.exit()
        elif symbol == key.R:
            # Toggle mouse capture
            self.camera.toggle_mouse_capture()
            
    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.RIGHT:
            self.camera.toggle_mouse_capture()
            
    def on_mouse_motion(self, x, y, dx, dy):
        self.camera.process_mouse_movement(x, y, dx, dy)
        
    def on_resize(self, width, height):
        """Handle window resize"""
        # Update viewport
        self.ctx.viewport = (0, 0, width, height)
        
        # Update projection matrix
        aspect_ratio = width / height
        fov = 45.0
        near = 0.1
        far = 100.0
        self.renderer.projection = self.renderer.create_perspective_projection(fov, aspect_ratio, near, far)
        self.renderer.prog['projection'].write(self.renderer.projection.tobytes())
        
        return True
        
    def on_draw(self):
        """Draw the scene"""
        self.clear()
        
        # Get current view matrix from camera
        view_matrix = self.camera.get_view_matrix()
        
        # Render with the current view matrix
        self.renderer.render(view_matrix)
        
        # Draw GUI
        self.gui.draw()
        
def main():
    app = FractalForestApp()
    pyglet.app.run()
    
if __name__ == "__main__":
    main()
