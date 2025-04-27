import pyglet
import numpy as np

class GUI:
    def __init__(self, window):
        self.window = window
        
        # Main instructions label
        self.label_instructions = pyglet.text.Label(
            "Controls: G - Generate new tree | W,A,S,D - Move camera | Right-click - Toggle mouse look",
            x=10, y=10,
            color=(0, 0, 0, 255)
        )
        
        # Tree info label
        self.label_tree_info = pyglet.text.Label(
            "Current tree: None",
            x=10, y=30,
            color=(0, 0, 0, 255)
        )
        
        # Camera position label
        self.label_camera_pos = pyglet.text.Label(
            "Camera Pos: (0.0, 0.0, 0.0)",
            x=10, y=50,
            color=(0, 0, 0, 255)
        )
        
        # Camera direction label
        self.label_camera_dir = pyglet.text.Label(
            "Camera Dir: (0.0, 0.0, -1.0)",
            x=10, y=70,
            color=(0, 0, 0, 255)
        )
        
        # Tree position label
        self.label_tree_pos = pyglet.text.Label(
            "Tree Center: (0.0, 0.0, 0.0)",
            x=10, y=90,
            color=(0, 0, 0, 255)
        )
        
        # Tree dimensions label
        self.label_tree_dim = pyglet.text.Label(
            "Tree Dimensions: (0.0, 0.0, 0.0)",
            x=10, y=110,
            color=(0, 0, 0, 255)
        )
        
        # Camera distance label
        self.label_camera_dist = pyglet.text.Label(
            "Distance to tree: 0.0",
            x=10, y=130,
            color=(0, 0, 0, 255)
        )
        
    def update_tree_info(self, tree_type):
        """Update the displayed tree information"""
        self.label_tree_info.text = f"Current tree: {tree_type.capitalize()}"
        
    def update_camera_info(self, camera_pos, camera_front):
        """Update the displayed camera information"""
        # Camera position
        x, y, z = camera_pos
        self.label_camera_pos.text = f"Camera Pos: ({x:.2f}, {y:.2f}, {z:.2f})"
        
        # Camera direction
        fx, fy, fz = camera_front
        self.label_camera_dir.text = f"Camera Dir: ({fx:.2f}, {fy:.2f}, {fz:.2f})"
        
        # Update tree info if available
        if hasattr(self.window, 'tree') and hasattr(self.window.tree, 'vertices'):
            vertices = self.window.tree.vertices[:, :3]  # Get just positions
            min_coords = np.min(vertices, axis=0)
            max_coords = np.max(vertices, axis=0)
            center = (min_coords + max_coords) / 2
            dimensions = max_coords - min_coords
            
            # Tree center
            self.label_tree_pos.text = f"Tree Center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})"
            
            # Tree dimensions
            self.label_tree_dim.text = f"Tree Dimensions: ({dimensions[0]:.2f}, {dimensions[1]:.2f}, {dimensions[2]:.2f})"
            
            # Distance from camera to tree center
            distance = np.linalg.norm(camera_pos - center)
            self.label_camera_dist.text = f"Distance to tree: {distance:.2f}"
    
    def draw(self):
        """Draw all GUI elements"""
        self.label_instructions.draw()
        self.label_tree_info.draw()
        self.label_camera_pos.draw()
        self.label_camera_dir.draw()
        self.label_tree_pos.draw()
        self.label_tree_dim.draw()
        self.label_camera_dist.draw()
