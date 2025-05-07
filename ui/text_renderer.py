"""
Text Renderer modul pro zobrazování textových informací na obrazovce pomocí moderngl-text.
"""
import moderngl
import moderngl_window as mglw
import moderngl_text as mtext
import numpy as np
import logging

class TextRenderer:
    """Třída pro zobrazování textových informací na obrazovce."""
    
    def __init__(self, ctx, window_size=(1366, 768), font_size=18):
        """
        Inicializuje text renderer.
        
        Args:
            ctx: moderngl kontext
            window_size: Velikost okna (šířka, výška)
            font_size: Velikost písma
        """
        self.logger = logging.getLogger(__name__)
        self.ctx = ctx
        self.window_size = window_size
        self.font_size = font_size
        
        try:
            # Inicializace text rendereru pomocí moderngl_text
            self.text_renderer = mtext.TextRenderer(
                ctx=self.ctx,
                font_size=self.font_size,
                font_name="NotoSans-Regular"  # Používáme standardní font
            )
            
            self.logger.info("Text renderer initialized successfully")
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize text renderer: {e}")
            self.text_renderer = None
    
    def render_text(self, text, position, color=(1.0, 1.0, 1.0, 1.0)):
        """
        Vykreslí text na dané pozici.
        
        Args:
            text: Text k vykreslení
            position: Pozice (x, y) - levý horní roh
            color: Barva textu (r, g, b, a)
        """
        if self.text_renderer is None:
            return
        
        try:
            x, y = position
            
            # Normalizace pozice na -1 až 1 (OpenGL koordináty)
            norm_x = (x / self.window_size[0]) * 2 - 1
            norm_y = 1 - (y / self.window_size[1]) * 2  # Inverzní pro y-osu
            
            self.text_renderer.render(text, pos=(norm_x, norm_y), color=color)
            
        except Exception as e:
            self.logger.exception(f"Error rendering text: {e}")
    
    def render_controls_info(self, position=(10, 10), controls=None):
        """
        Vykreslí informace o ovládání.
        
        Args:
            position: Pozice levého horního rohu (x, y)
            controls: Slovník s ovládáním {klávesa: popis}
        """
        if controls is None:
            controls = {
                "G": "Generovat strom",
                "F": "Generovat les",
                "N/M": "Hustota lesa -/+",
                "K/L": "Velikost lesa -/+",
                "WASD": "Pohyb kamery",
                "QE": "Nahoru/Dolů",
                "RMB": "Rozhlížení",
                "ESC": "Konec"
            }
        
        x, y = position
        line_height = self.font_size + 5
        
        for i, (key, desc) in enumerate(controls.items()):
            self.render_text(f"{key}: {desc}", (x, y + i * line_height), color=(0.9, 0.9, 0.2, 1.0))
    
    def render_tree_info(self, tree_name=None, position=(10, 200)):
        """
        Vykreslí informace o aktuálním stromu.
        
        Args:
            tree_name: Název typu stromu
            position: Pozice (x, y)
        """
        if tree_name:
            self.render_text(f"Aktuální strom: {tree_name}", position, color=(0.2, 0.9, 0.2, 1.0))
    
    def render_forest_info(self, trees_count=None, tree_types=None, position=(10, 200)):
        """
        Vykreslí informace o aktuálním lese.
        
        Args:
            trees_count: Celkový počet stromů v lese
            tree_types: Slovník {typ_stromu: počet}
            position: Pozice (x, y)
        """
        if trees_count is None or tree_types is None:
            return
        
        x, y = position
        line_height = self.font_size + 5
        
        self.render_text(f"Les: {trees_count} stromů", (x, y), color=(0.2, 0.7, 0.9, 1.0))
        
        for i, (tree_type, count) in enumerate(tree_types.items()):
            self.render_text(f"- {tree_type}: {count}x", (x, y + (i+1) * line_height), color=(0.2, 0.9, 0.2, 1.0))
    
    def render_fps(self, fps, position=(10, 700)):
        """
        Vykreslí FPS.
        
        Args:
            fps: Počet snímků za sekundu
            position: Pozice (x, y)
        """
        self.render_text(f"FPS: {fps:.1f}", position, color=(0.9, 0.9, 0.9, 1.0))
