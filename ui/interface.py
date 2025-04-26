"""
Modul pro uživatelské rozhraní
"""
import pyglet

class Interface:
    """Třída pro správu uživatelského rozhraní"""
    
    def __init__(self):
        """Inicializace UI"""
        # Font pro text
        self.font = pyglet.font.load('Arial', 14)
        
        # Příznak, zda zobrazit nastavení
        self.show_settings = True
        
        # Nastavení parametrů lesa
        self.forest_params = {
            'size': 50,
            'density': 0.5,
            'tree_types': ['pine', 'oak', 'bush'],
            'season': 'summer'
        }
        
        # Připravení textových popisků
        self.labels = {
            'title': pyglet.text.Label(
                'FractalForest', font_name='Arial', font_size=20,
                x=10, y=700, color=(255, 255, 255, 255)
            ),
            'controls': pyglet.text.Label(
                'Ovládání: WASD - pohyb, myš - rozhlížení, G - nový les, TAB - změna módu',
                font_name='Arial', font_size=12,
                x=10, y=20, color=(255, 255, 255, 200)
            ),
            'params': {}
        }
        
        # Vytvoření popisků pro parametry
        y_pos = 650
        for param in ['size', 'density']:
            self.labels['params'][param] = pyglet.text.Label(
                f"{param}: {self.forest_params[param]}",
                font_name='Arial', font_size=14,
                x=10, y=y_pos, color=(255, 255, 255, 255)
            )
            y_pos -= 30
            
        # Popisek pro typy stromů
        self.labels['params']['tree_types'] = pyglet.text.Label(
            f"tree_types: {', '.join(self.forest_params['tree_types'])}",
            font_name='Arial', font_size=14,
            x=10, y=y_pos, color=(255, 255, 255, 255)
        )
        y_pos -= 30
        
        # Popisek pro roční období
        self.labels['params']['season'] = pyglet.text.Label(
            f"season: {self.forest_params['season']}",
            font_name='Arial', font_size=14,
            x=10, y=y_pos, color=(255, 255, 255, 255)
        )
        
    def toggle_settings(self):
        """Přepne zobrazení nastavení"""
        self.show_settings = not self.show_settings
        
    def update_params(self, params):
        """
        Aktualizuje parametry a popisky
        
        Parametry:
        - params: slovník s novými parametry
        """
        # Aktualizace hodnot
        self.forest_params.update(params)
        
        # Aktualizace popisků
        for param in ['size', 'density', 'season']:
            if param in self.labels['params']:
                self.labels['params'][param].text = f"{param}: {self.forest_params[param]}"
                
        # Speciální případ pro seznam typů stromů
        if 'tree_types' in self.labels['params']:
            self.labels['params']['tree_types'].text = f"tree_types: {', '.join(self.forest_params['tree_types'])}"
        
    def draw(self):
        """Vykreslí UI elementy"""
        if not self.show_settings:
            # Pokud nezobrazujeme nastavení, zobrazíme jen ovládání
            self.labels['controls'].draw()
            return
            
        # Vykreslení poloprůhledného pozadí pro nastavení
        width = 250
        height = 200
        
        # Vykreslení popisků
        self.labels['title'].draw()
        self.labels['controls'].draw()
        
        # Vykreslení parametrů
        for label in self.labels['params'].values():
            label.draw()
