"""
Text rendering module for displaying text information on screen using moderngl_window.Text.
"""
import moderngl_window as mglw
from moderngl_window import text
import logging

class TextRenderer:
    """Class for rendering text information on screen using moderngl_window.Text."""
    
    def __init__(self, ctx, window_size=(1366, 768), font_size=18):
        """
        Initializes the text renderer.
        
        Args:
            ctx: moderngl context
            window_size: Window size (width, height)
            font_size: Font size
        """
        self.logger = logging.getLogger(__name__)
        self.ctx = ctx
        self.window_size = window_size
        self.font_size = font_size
        self.text_instances = {}
        
        try:
            # Load a font (this creates a texture atlas)
            self.font = mglw.resources.fonts.load(
                "NotoSans-Regular.ttf",
                size=self.font_size,
                charset="iso-8859-2"
            )
            self.logger.info("Text renderer initialized successfully")
        except Exception as e:
            self.logger.exception(f"Failed to initialize text renderer: {e}")
            self.font = None
    
    def render_text(self, text, position, color=(1.0, 1.0, 1.0, 1.0)):
        """
        Renders text at the given position.
        
        Args:
            text: Text to render
            position: Position (x, y) - top-left corner
            color: Text color (r, g, b, a)
        """
        if self.font is None:
            return
        
        try:
            x, y = position
            
            # Create a new Text instance if we don't have one for this text
            if text not in self.text_instances:
                self.text_instances[text] = Text(
                    text=text,
                    font=self.font,
                    color=color,
                    pos=(x, y),
                )
            
            # Update position and color if needed
            text_instance = self.text_instances[text]
            text_instance.pos = (x, y)
            text_instance.color = color
            
            # Render the text
            text_instance.draw()
            
        except Exception as e:
            self.logger.exception(f"Error rendering text: {e}")
    
    def render_controls_info(self, position=(10, 10), controls=None):
        """
        Renders control information.
        
        Args:
            position: Top-left corner position (x, y)
            controls: Dictionary with controls {key: description}
        """
        if controls is None:
            controls = {
                "G": "Generate tree",
                "F": "Generate forest",
                "N/M": "Forest density -/+",
                "K/L": "Forest size -/+",
                "WASD": "Camera movement",
                "QE": "Up/Down",
                "RMB": "Look around",
                "ESC": "Exit"
            }
        
        x, y = position
        line_height = self.font_size + 5
        
        for i, (key, desc) in enumerate(controls.items()):
            self.render_text(f"{key}: {desc}", (x, y + i * line_height), color=(0.9, 0.9, 0.2, 1.0))
    
    def render_tree_info(self, tree_name=None, position=(10, 200)):
        """
        Renders information about the current tree.
        
        Args:
            tree_name: Name of the tree type
            position: Position (x, y)
        """
        if tree_name:
            self.render_text(f"Current tree: {tree_name}", position, color=(0.2, 0.9, 0.2, 1.0))
    
    def render_forest_info(self, trees_count=None, tree_types=None, position=(10, 200)):
        """
        Renders information about the current forest.
        
        Args:
            trees_count: Total number of trees in the forest
            tree_types: Dictionary {tree_type: count}
            position: Position (x, y)
        """
        if trees_count is None or tree_types is None:
            return
        
        x, y = position
        line_height = self.font_size + 5
        
        self.render_text(f"Forest: {trees_count} trees", (x, y), color=(0.2, 0.7, 0.9, 1.0))
        
        for i, (tree_type, count) in enumerate(tree_types.items()):
            self.render_text(f"- {tree_type}: {count}x", (x, y + (i+1) * line_height), color=(0.2, 0.9, 0.2, 1.0))
    
    def render_fps(self, fps, position=(10, 700)):
        """
        Renders FPS counter.
        
        Args:
            fps: Frames per second
            position: Position (x, y)
        """
        self.render_text(f"FPS: {fps:.1f}", position, color=(0.9, 0.9, 0.9, 1.0))
