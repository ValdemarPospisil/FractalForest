import imgui
import numpy as np
import logging

class TreeInfoDisplay:
    """Class for displaying information about the generated tree in ImGui."""
    
    def __init__(self):
        """Initialize the tree info display."""
        self.tree_data = {
            "name": "No tree generated yet",
            "axiom": "",
            "iterations": 0,
            "angle": 0.0,
            "thickness_ratio": 0.0,
            "length_ratio": 0.0,
            "base_length": 0.0,
            "base_thickness": 0.0,
            "color": [0.0, 0.0, 0.0, 1.0],
            "vertex_count": 0,
            "string_length": 0
        }
        self.visible = True
        logging.info("Tree info display initialized")
    
    def update(self, tree_properties):
        """Update the tree information to display."""
        self.tree_data.update(tree_properties)
        logging.info(f"Tree info display updated with {tree_properties['name']} data")
    
    def toggle_visibility(self):
        """Toggle the visibility of the info display."""
        self.visible = not self.visible
        logging.info(f"Tree info display visibility: {'Shown' if self.visible else 'Hidden'}")
    
    def render(self):
        """Render the tree information using ImGui."""
        if not self.visible:
            return
            
        # Start a new ImGui window
        imgui.begin("Tree Information", True)
        
        # Display tree type name
        imgui.text_colored(0.5, 1.0, 0.5, 1.0, f"Type: {self.tree_data['name']}")
        imgui.separator()
        
        # Basic properties section
        if imgui.collapsing_header("Basic Properties", True):
            imgui.text(f"Axiom: {self.tree_data['axiom']}")
            imgui.text(f"Iterations: {self.tree_data['iterations']}")
            imgui.text(f"Angle: {self.tree_data['angle']:.2f}°")
            
            # Color display
            color = self.tree_data['color']
            imgui.text("Trunk Color:")
            imgui.same_line()
            imgui.color_button("##color", color[0], color[1], color[2], color[3], 0, 15, 15)
        
        # Technical details section
        if imgui.collapsing_header("Technical Details", True):
            imgui.text(f"Thickness Ratio: {self.tree_data['thickness_ratio']:.2f}")
            imgui.text(f"Length Ratio: {self.tree_data['length_ratio']:.2f}")
            imgui.text(f"Base Length: {self.tree_data['base_length']:.2f}")
            imgui.text(f"Base Thickness: {self.tree_data['base_thickness']:.2f}")
        
        # Rendering stats section
        if imgui.collapsing_header("Rendering Stats", True):
            imgui.text(f"Vertex Count: {self.tree_data['vertex_count']:,}")
            imgui.text(f"L-system String Length: {self.tree_data['string_length']:,}")
            
            # Draw a simple vertex count bar
            max_vertices = 50000  # Approximate maximum for scale
            ratio = min(1.0, self.tree_data['vertex_count'] / max_vertices)
            imgui.text("Vertex Count:")
            imgui.progress_bar(ratio, (0, 0), f"{self.tree_data['vertex_count']:,}/{max_vertices:,}")
        
        # Controls reminder
        imgui.separator()
        imgui.text_colored(0.9, 0.9, 0.4, 1.0, "Controls:")
        imgui.bullet_text("SPACE - Generate new random tree")
        imgui.bullet_text("1-5 - Select specific tree type")
        imgui.bullet_text("I - Toggle this info panel")
        imgui.bullet_text("ESC - Exit")
        
        # End the ImGui window
        imgui.end()

# If imgui is not available, create a simple fallback implementation
try:
    import imgui
except ImportError:
    logging.warning("ImGui not available. Using fallback console tree info display.")
    
    class TreeInfoDisplay:
        """Fallback class that just logs tree information."""
        
        def __init__(self):
            self.tree_data = {}
            logging.info("Using fallback console tree info display (ImGui not available)")
        
        def update(self, tree_properties):
            """Update tree data and log it."""
            self.tree_data = tree_properties
            logging.info("=== Tree Information ===")
            for key, value in tree_properties.items():
                logging.info(f"{key}: {value}")
            logging.info("=======================")
        
        def toggle_visibility(self):
            """Does nothing in fallback implementation."""
            pass
            
        def render(self):
            """Does nothing in fallback implementation."""
            pass
