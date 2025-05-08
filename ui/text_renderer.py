"""
Text rendering module for displaying text information on screen using DearPyGUI.
"""
import dearpygui.dearpygui as dpg
import logging

class TextRenderer:
    def __init__(self, ctx=None, window_size=(1366, 768), font_size=18):
        self.logger = logging.getLogger(__name__)
        self.window_size = window_size
        self.font_size = font_size
        self.text_items = {}
        self.is_initialized = False
        
        try:
            # Don't create new context - assume it's created by main application
            if not dpg.is_dearpygui_running():
                self.logger.error("DearPyGUI context not created!")
                return
                
            # Create overlay window
            with dpg.window(label="Text Overlay", tag="text_overlay", 
                           no_title_bar=True, no_resize=True, no_move=True,
                           no_collapse=True, no_close=True,
                           width=window_size[0], height=window_size[1]):
                pass
            
            dpg.set_viewport_clear_color([0, 0, 0, 0])  # Transparent background
            self.is_initialized = True
            self.logger.info("Text renderer initialized")
        except Exception as e:
            self.logger.exception(f"Failed to initialize text renderer: {e}")
    
    def render_text(self, text, position, color=(1.0, 1.0, 1.0, 1.0)):
        """
        Renders text at the given position.
        
        Args:
            text: Text to render
            position: Position (x, y) - top-left corner
            color: Text color (r, g, b, a)
        """
        if not self.is_initialized:
            return
        
        try:
            x, y = position
            text_id = f"text_{x}_{y}_{hash(text)}"  # Using hash to create unique ID
            
            # Convert color from 0-1 to 0-255 range
            dpg_color = [int(c * 255) for c in color]
            
            # Create or update text item
            if text_id not in self.text_items:
                self.text_items[text_id] = dpg.add_text(
                    text,
                    parent="text_overlay",
                    pos=(x, y),
                    color=dpg_color
                )
            else:
                dpg.set_value(self.text_items[text_id], text)
                dpg.set_item_pos(self.text_items[text_id], (x, y))
                dpg.configure_item(self.text_items[text_id], color=dpg_color)
                
        except Exception as e:
            self.logger.exception(f"Error rendering text with DearPyGUI: {e}")
    
    # ... rest of your methods remain the same ...


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
    
    def clear_text(self):
        """
        Clears all text from the screen.
        """
        if not self.is_initialized:
            return
            
        try:
            for text_id in self.text_items.values():
                dpg.delete_item(text_id)
            self.text_items = {}
        except Exception as e:
            self.logger.exception(f"Error clearing text: {e}")
    
    def update(self):
        """
        Updates the DearPyGUI renderer. This should be called each frame.
        """
        if not self.is_initialized:
            return
            
        try:
            dpg.render_dearpygui_frame()
        except Exception as e:
            self.logger.exception(f"Error updating DearPyGUI: {e}")
