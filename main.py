#!/usr/bin/env python3
"""
FractalForest - Procedurální generátor lesů pomocí L-systémů
Hlavní spouštěcí soubor
"""
import os
import sys
import pyglet
import moderngl
from engine.renderer import Renderer
from engine.camera import Camera
from generation.forest import Forest
from ui import interface
from ui.interface import Interface

class FractalForest:
    """Hlavní třída aplikace"""
    
    def __init__(self):
        # Vytvoření okna
        self.window = pyglet.window.Window(width=1280, height=720, caption="FractalForest")
        
        # Inicializace ModernGL kontextu
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        
        # Inicializace kamery
        self.camera = Camera(self.window.width, self.window.height)
        
        # Inicializace rendereru
        self.renderer = Renderer(self.ctx, self.camera)
        
        # Inicializace uživatelského rozhraní
        self.interface = Interface()
        
        # Základní parametry lesa
        self.forest_params = {
            'size': 50,
            'density': 0.5,
            'tree_types': ['pine', 'oak', 'bush'],
            'season': 'summer'
        }
        
        # Inicializace lesa
        self.forest = None
        self.generate_forest()
        
        # Nastavení eventů
        self.setup_events()
        
        # Flag pro režim procházení
        self.walk_mode = False
        
        # Nastavení klávesnice pro ovládání kamery
        self.keys = pyglet.window.key.KeyStateHandler()
        self.window.push_handlers(self.keys)
        
        # Nastavení časovače pro aktualizaci kamery
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        
    def generate_forest(self):
        """Generuje nový les podle aktuálních parametrů"""
        self.forest = Forest(
            size=self.forest_params['size'],
            density=self.forest_params['density'],
            tree_types=self.forest_params['tree_types'],
            season=self.forest_params['season']
        )
        self.forest.generate()
        
        # Důležité: Vytvoření VAO pro všechny stromy v lese
        # Toto je kritický krok, který chyběl - připraví geometrie stromů pro vykreslení
        for tree in self.forest.trees:
            self.renderer.create_tree_vao(tree)
        
    def setup_events(self):
        """Nastavení event handlerů pro pyglet"""
        @self.window.event
        def on_resize(width, height):
            self.ctx.viewport = (0, 0, width, height)
            self.camera.update_projection(width, height)
            
        @self.window.event
        def on_draw():
            self.ctx.clear(0.5, 0.7, 1.0)
            self.renderer.render(self.forest)
            
            # Vykreslení UI
            self.interface.draw()
            
        @self.window.event
        def on_key_press(symbol, modifiers):
            # Pohyb kamery je nyní řešen v update()
                
            # Přepnutí režimu
            if symbol == pyglet.window.key.TAB:
                self.walk_mode = not self.walk_mode
                if self.walk_mode:
                    self.camera.set_walk_mode()
                else:
                    self.camera.set_fly_mode()
                    
            # Generování nového lesa
            elif symbol == pyglet.window.key.G:
                self.generate_forest()
                
            # Ukončení aplikace
            elif symbol == pyglet.window.key.ESCAPE:
                pyglet.app.exit()
                
        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            # Otáčení kamery pomocí myši - necháme aktivní bez ohledu na režim
            self.camera.rotate(dx, dy)
    
    def update(self, dt):
        """Aktualizuje stav aplikace (pohyb kamery)"""
        # Zpracování pohybu kamery podle stisknutých kláves
        if self.keys[pyglet.window.key.W]:
            self.camera.move_forward()
        if self.keys[pyglet.window.key.S]:
            self.camera.move_backward()
        if self.keys[pyglet.window.key.A]:
            self.camera.move_left()
        if self.keys[pyglet.window.key.D]:
            self.camera.move_right()
                
    def run(self):
        """Spustí hlavní smyčku aplikace"""
        pyglet.app.run()
        
if __name__ == "__main__":
    app = FractalForest()
    app.run()
