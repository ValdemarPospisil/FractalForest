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
        if self.camera == None:
            print("camera is null")
        # Inicializace rendereru
        self.renderer = Renderer(self.ctx, self.camera)
        if self.renderer == None:
            print("renderer is null")
        # Inicializace uživatelského rozhraní
        self.interface = Interface()
        if self.interface == None:
            print("Interface is null")
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
        
    def generate_forest(self):
        """Generuje nový les podle aktuálních parametrů"""
        self.forest = Forest(
            size=self.forest_params['size'],
            density=self.forest_params['density'],
            tree_types=self.forest_params['tree_types'],
            season=self.forest_params['season']
        )
        self.forest.generate()
        
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
            
        @self.window.event
        def on_key_press(symbol, modifiers):
            # Pohyb kamery
            if symbol == pyglet.window.key.W:
                self.camera.move_forward()
            elif symbol == pyglet.window.key.S:
                self.camera.move_backward()
            elif symbol == pyglet.window.key.A:
                self.camera.move_left()
            elif symbol == pyglet.window.key.D:
                self.camera.move_right()
                
            # Přepnutí režimu
            elif symbol == pyglet.window.key.TAB:
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
            if self.walk_mode:
                self.camera.rotate(dx, dy)
                
    def run(self):
        """Spustí hlavní smyčku aplikace"""
        pyglet.app.run()
        
if __name__ == "__main__":
    app = FractalForest()
    app.run()
