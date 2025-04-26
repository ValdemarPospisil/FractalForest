import pyglet

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
        self.label_camera = pyglet.text.Label(
            "Camera: (0.0, 0.0, 3.0)",
            x=10, y=50,
            color=(0, 0, 0, 255)
        )
        
    def update_tree_info(self, tree_type):
        """Update the displayed tree information"""
        self.label_tree_info.text = f"Current tree: {tree_type.capitalize()}"
        
    def update_camera_info(self, position):
        """Update the displayed camera information"""
        x, y, z = position
        self.label_camera.text = f"Camera: ({x:.1f}, {y:.1f}, {z:.1f})"
    
    def draw(self):
        """Draw all GUI elements"""
        self.label_instructions.draw()
        self.label_tree_info.draw()
        self.label_camera.draw()
