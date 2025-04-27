import pyglet
import moderngl
import random
import logging
import numpy as np
from pyglet.window import key
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
logger = logging.getLogger(__name__)

# Available tree types
TREE_TYPES = ["pine", "oak", "bush"]

class FractalForestApp(pyglet.window.Window):
    def __init__(self, width=1280, height=720):
        super().__init__(width, height, "FractalForest")
        self.ctx = moderngl.create_context()
        self.renderer = Renderer(self.ctx)
        self.gui = GUI(self)
        
        # Camera settings
        self.camera_pos = np.array([5.0, 8.0, 8.0], dtype='f4')  # Slightly higher Y to look at tree better
        self.camera_front = np.array([0.0, 1.5, 0.0], dtype='f4')
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype='f4')
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_x = width / 2
        self.last_y = height / 2
        self.first_mouse = True
        self.mouse_sensitivity = 0.1
        
        # Camera movement
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.camera_speed = 0.05

        # Generate initial tree
        self.generate_random_tree()
        
        # Enable mouse capture for camera control (right-click)
        self.mouse_captured = False
        
        # Setup update function for camera movement processing
        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def update(self, dt):
        """Process camera movement"""
        if not self.mouse_captured:
            return
            
        camera_speed = self.camera_speed * dt * 60
        
        # Forward/backward
        if self.keys[key.W]:
            self.camera_pos += camera_speed * self.camera_front
        if self.keys[key.S]:
            self.camera_pos -= camera_speed * self.camera_front
            
        # Left/right
        if self.keys[key.A]:
            right = np.cross(self.camera_front, self.camera_up)
            right = right / np.linalg.norm(right)
            self.camera_pos -= right * camera_speed
        if self.keys[key.D]:
            right = np.cross(self.camera_front, self.camera_up)
            right = right / np.linalg.norm(right)
            self.camera_pos += right * camera_speed
            
        # Up/down
        if self.keys[key.SPACE]:
            self.camera_pos[1] += camera_speed
        if self.keys[key.LSHIFT]:
            self.camera_pos[1] -= camera_speed
    
    def generate_random_tree(self):
        """Generate a random tree from available types"""
        tree_type = random.choice(TREE_TYPES)
        logger.info(f"Generating new tree of type: {tree_type}")
        
        # Set specific parameters based on tree type
        if tree_type == "pine":
            iterations = 4
            angle = 22.5
            length = 0.03
            color = (0.1, 0.4, 0.1)  # Dark green
        elif tree_type == "oak":
            iterations = 4
            angle = 25.0
            length = 0.04
            color = (0.3, 0.5, 0.2)  # Medium green
        elif tree_type == "bush":
            iterations = 3
            angle = 28.0
            length = 0.05
            color = (0.4, 0.6, 0.3)  # Light green
            
        # Generate L-system and tree
        lsystem = LSystem.create_tree_system(tree_type=tree_type, randomness=0.15)
        instructions = lsystem.generate(iterations)
        self.tree = Tree(instructions, angle=angle, length=length, tree_type=tree_type)
        
        # Update renderer with tree and color
        self.renderer.update_tree(self.tree)
        self.renderer.color = color
        
        # Update GUI with tree type info
        self.gui.update_tree_info(tree_type)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.G:
            self.generate_random_tree()
        elif symbol == key.ESCAPE:
            pyglet.app.exit()
        elif symbol == key.R:
            # Right click toggle
            self.toggle_mouse_capture()
            
    def toggle_mouse_capture(self):
        self.mouse_captured = not self.mouse_captured
        self.set_exclusive_mouse(self.mouse_captured)
            
    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.RIGHT:
            self.toggle_mouse_capture()
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Zoom in/out with mouse wheel"""
        self.camera_pos += self.camera_front * scroll_y * 0.5

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.mouse_captured:
            return
            
        dx *= self.mouse_sensitivity
        dy *= self.mouse_sensitivity
        
        self.yaw += dx
        self.pitch -= dy
        
        # Constrain pitch
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
            
        # Calculate new front vector
        front = np.zeros(3, dtype='f4')
        front[0] = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        front[1] = np.sin(np.radians(self.pitch))
        front[2] = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.camera_front = front / np.linalg.norm(front)
        
    def create_view_matrix(self):
        """Create a view matrix from camera position, target and up vector"""
        target = self.camera_pos + self.camera_front
        return self.look_at(self.camera_pos, target, self.camera_up)
        
    def look_at(self, eye, target, up):
        """Create a look-at matrix"""
        eye = np.array(eye, dtype='f4')
        target = np.array(target, dtype='f4')
        up = np.array(up, dtype='f4')
        
        f = target - eye
        f = f / np.linalg.norm(f)
        
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        
        u = np.cross(s, f)
        
        result = np.identity(4, dtype='f4')
        result[0, 0] = s[0]
        result[0, 1] = s[1]
        result[0, 2] = s[2]
        result[1, 0] = u[0]
        result[1, 1] = u[1]
        result[1, 2] = u[2]
        result[2, 0] = -f[0]
        result[2, 1] = -f[1]
        result[2, 2] = -f[2]
        result[0, 3] = -np.dot(s, eye)
        result[1, 3] = -np.dot(u, eye)
        result[2, 3] = np.dot(f, eye)
        
        return result
        
    def on_draw(self):
        """Draw the scene"""
        self.clear()
        
       
        # Create view matrix for the camera
        view_matrix = self.create_view_matrix()
    
        # Render the tree with the current view
        self.renderer.render(view_matrix)
    
        # Update GUI with camera info
        self.gui.update_camera_info(self.camera_pos, self.camera_front)

        # Draw GUI on top
        self.gui.draw()
        
def main():
    app = FractalForestApp(1280, 720)
    pyglet.app.run()
    
if __name__ == "__main__":
    main()
