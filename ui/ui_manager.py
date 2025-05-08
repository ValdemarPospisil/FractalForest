"""
UI Manager pro koordinaci zobrazování informací na obrazovce pomocí DearPyGUI.
"""
import logging
import dearpygui.dearpygui as dpg
from .text_renderer import TextRenderer

class UIManager:
    """Třída pro správu UI prvků a zobrazování informací na obrazovce."""
    
    def __init__(self, ctx, window_size=(1366, 768)):
        """
        Inicializuje UI manager.
        
        Args:
            ctx: moderngl kontext
            window_size: Velikost okna (šířka, výška)
        """
        self.logger = logging.getLogger(__name__)
        self.ctx = ctx
        self.window_size = window_size
        
        # Základní nastavení
        self.show_controls = True
        self.show_fps = True
        self.forest_mode = False
        self.current_tree = None
        self.forest_info = None
        
        # Inicializace text rendereru
        self.text_renderer = TextRenderer(ctx, window_size)
        
        # Základní ovládání
        self.controls = {
            "G": "Generovat strom",
            "F": "Generovat les",
            "N/M": "Hustota lesa -/+",
            "K/L": "Velikost lesa -/+",
            "WASD+QE": "Pohyb kamery",
            "RMB": "Rozhlížení",
            "H": "Zobrazit/skrýt ovládání",
            "P": "Zobrazit/skrýt FPS",
            "ESC": "Konec"
        }
        
        self.logger.info("UI Manager initialized with DearPyGUI")
    
    def set_forest_mode(self, enabled):
        """
        Nastaví režim zobrazování lesa.
        
        Args:
            enabled: True pokud je aktivní režim lesa, jinak False
        """
        self.forest_mode = enabled
        self.logger.debug(f"Forest mode set to {enabled}")
    
    def set_current_tree(self, tree_name):
        """
        Nastaví aktuální strom.
        
        Args:
            tree_name: Název typu stromu
        """
        self.current_tree = tree_name
        self.logger.debug(f"Current tree set to {tree_name}")
    
    def set_forest_info(self, trees_count, tree_types):
        """
        Nastaví informace o lese.
        
        Args:
            trees_count: Celkový počet stromů v lese
            tree_types: Slovník {typ_stromu: počet}
        """
        self.forest_info = {
            'count': trees_count,
            'types': tree_types
        }
        self.logger.debug(f"Forest info updated: {trees_count} trees")
    
    def toggle_controls_visibility(self):
        """Přepne viditelnost ovládacích prvků."""
        self.show_controls = not self.show_controls
        self.logger.debug(f"Controls visibility set to {self.show_controls}")
    
    def toggle_fps_visibility(self):
        """Přepne viditelnost FPS."""
        self.show_fps = not self.show_fps
        self.logger.debug(f"FPS visibility set to {self.show_fps}")
    
    def render(self, fps=None):
        """
        Vykreslí všechny UI prvky.
        
        Args:
            fps: Aktuální snímková frekvence (volitelné)
        """
        try:
            # Nejprve vyčistíme text, abychom zamezili překrývání
            self.text_renderer.clear_text()
            
            # Zobrazení ovládání
            if self.show_controls:
                self.text_renderer.render_controls_info(position=(10, 10), controls=self.controls)
            
            # Zobrazení informací o stromu nebo lese
            if self.forest_mode and self.forest_info:
                self.text_renderer.render_forest_info(
                    trees_count=self.forest_info['count'],
                    tree_types=self.forest_info['types'],
                    position=(10, 200)
                )
            elif self.current_tree:
                self.text_renderer.render_tree_info(
                    tree_name=self.current_tree,
                    position=(10, 200)
                )
            
            # Zobrazení FPS
            if self.show_fps and fps is not None:
                self.text_renderer.render_fps(fps, position=(self.window_size[0] - 120, 10))
            
            # Aktualizace DearPyGUI
            self.text_renderer.update()
                
        except Exception as e:
            self.logger.exception(f"Error rendering UI: {e}")
    
    def cleanup(self):
        """Uvolnění prostředků DearPyGUI."""
        try:
            if dpg.is_dearpygui_running():
                dpg.destroy_context()
            self.logger.info("DearPyGUI context destroyed")
        except Exception as e:
            self.logger.exception(f"Error during DearPyGUI cleanup: {e}")
