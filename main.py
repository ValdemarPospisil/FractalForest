#!/usr/bin/env python3
"""
FractalForest - Procedurální generátor lesů pomocí L-systémů
Hlavní spouštěcí soubor
"""
import os
import sys
import logging
import pyglet
import moderngl
from engine.renderer import Renderer
from engine.camera import Camera
from generation.forest import Forest
from ui import interface
from ui.interface import Interface

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fractalforest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FractalForest')

class FractalForest:
    """Hlavní třída aplikace"""
    
    def __init__(self):
        logger.info("Initializing FractalForest application")
        
        # Vytvoření okna
        self.window = pyglet.window.Window(width=1280, height=720, caption="FractalForest")
        logger.debug(f"Window created with dimensions {self.window.width}x{self.window.height}")
        
        # Inicializace ModernGL kontextu
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        logger.debug("ModernGL context created with DEPTH_TEST and CULL_FACE enabled")
        
        # Inicializace kamery
        self.camera = Camera(self.window.width, self.window.height)
        logger.debug(f"Camera initialized at position {self.camera.position}")
        
        # Inicializace rendereru
        self.renderer = Renderer(self.ctx, self.camera)
        logger.debug("Renderer initialized")
        
        # Inicializace uživatelského rozhraní
        self.interface = Interface()
        logger.debug("UI interface initialized")
        
        # Základní parametry lesa
        self.forest_params = {
            'size': 50,
            'density': 0.5,
            'tree_types': ['pine', 'oak', 'bush'],
            'season': 'summer'
        }
        logger.info(f"Forest parameters set: {self.forest_params}")
        
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
        logger.info("FractalForest initialization complete")
        
    def generate_forest(self):
        """Generuje nový les podle aktuálních parametrů"""
        logger.info("Generating new forest")
        self.forest = Forest(
            size=self.forest_params['size'],
            density=self.forest_params['density'],
            tree_types=self.forest_params['tree_types'],
            season=self.forest_params['season']
        )
        logger.debug("Forest object created")
        
        self.forest.generate()
        logger.info(f"Generated forest with {len(self.forest.trees)} trees")
        
        # Log information about the first few trees
        for i, tree in enumerate(self.forest.trees[:3]):
            logger.debug(f"Tree {i}: type={tree.tree_type}, position={tree.position}, scale={tree.scale}")
            if tree.geometry is not None:
                vertices, normals, indices = tree.geometry
                logger.debug(f"  - Geometry: {len(vertices)} vertices, {len(indices)} indices")
            else:
                logger.warning(f"  - Tree {i} has no geometry")
        
        # Create VAOs for all trees
        logger.info("Creating VAOs for all trees")
        vao_count = 0
        for i, tree in enumerate(self.forest.trees):
            self.renderer.create_tree_vao(tree)
            if tree.vao is not None:
                vao_count += 1
        
        logger.info(f"Successfully created {vao_count}/{len(self.forest.trees)} VAOs")
        
    def setup_events(self):
        """Nastavení event handlerů pro pyglet"""
        logger.debug("Setting up event handlers")
        
        @self.window.event
        def on_resize(width, height):
            logger.debug(f"Window resized to {width}x{height}")
            self.ctx.viewport = (0, 0, width, height)
            self.camera.update_projection(width, height)
            
        @self.window.event
        def on_draw():
            self.ctx.clear(0.5, 0.7, 1.0)
            
            # Debug camera position before rendering
            logger.debug(f"Camera position: {self.camera.position}, looking at: {self.camera.forward}")
            
            if self.forest and len(self.forest.trees) > 0:
                self.renderer.render(self.forest)
                logger.debug("Forest rendered")
            else:
                logger.warning("No forest to render")
            
            # Vykreslení UI
            self.interface.draw()
            
        @self.window.event
        def on_key_press(symbol, modifiers):
            # Debug key presses
            key_name = pyglet.window.key.symbol_string(symbol)
            logger.debug(f"Key pressed: {key_name}")
            
            # Přepnutí režimu
            if symbol == pyglet.window.key.TAB:
                self.walk_mode = not self.walk_mode
                if self.walk_mode:
                    self.camera.set_walk_mode()
                    logger.info("Camera mode changed to WALK")
                else:
                    self.camera.set_fly_mode()
                    logger.info("Camera mode changed to FLY")
                    
            # Generování nového lesa
            elif symbol == pyglet.window.key.G:
                logger.info("Regenerating forest")
                self.generate_forest()
                
            # Ukončení aplikace
            elif symbol == pyglet.window.key.ESCAPE:
                logger.info("Application exit requested")
                pyglet.app.exit()
                
        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            # We don't want to log every mouse movement as it would flood the logs
            # Only log significant rotations
            if abs(dx) > 20 or abs(dy) > 20:
                logger.debug(f"Camera rotated: dx={dx}, dy={dy}")
            self.camera.rotate(dx, dy)
    
    def update(self, dt):
        """Aktualizuje stav aplikace (pohyb kamery)"""
        # Log only significant camera movements
        movement = False
        
        if self.keys[pyglet.window.key.W]:
            self.camera.move_forward()
            movement = True
        if self.keys[pyglet.window.key.S]:
            self.camera.move_backward()
            movement = True
        if self.keys[pyglet.window.key.A]:
            self.camera.move_left()
            movement = True
        if self.keys[pyglet.window.key.D]:
            self.camera.move_right()
            movement = True
            
        if movement:
            logger.debug(f"Camera moved to {self.camera.position}")
                
    def run(self):
        """Spustí hlavní smyčku aplikace"""
        logger.info("Starting application main loop")
        pyglet.app.run()
        
if __name__ == "__main__":
    logger.info("Application starting")
    app = FractalForest()
    app.run()
