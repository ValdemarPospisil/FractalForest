#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glfw
import moderngl
import numpy as np
import random
import sys
import os

# Přidání cesty k modulům
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generation.lsystem import LSystem
from generation.tree import TreeType1, TreeType2
from engine.renderer import Renderer
from engine.camera import Camera

class Application:
    def __init__(self, width=800, height=600):
        # Inicializace GLFW
        if not glfw.init():
            raise RuntimeError("Nelze inicializovat GLFW")

        # Konfigurace GLFW
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.SAMPLES, 4)  # Anti-aliasing

        # Vytvoření okna
        self.window = glfw.create_window(width, height, "L-System 3D Trees", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Nelze vytvořit GLFW okno")

        # Nastavení okna jako aktuálního OpenGL kontextu
        glfw.make_context_current(self.window)
        
        # Nastavení callbacků
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_framebuffer_size_callback(self.window, self.resize_callback)

        # Inicializace ModernGL
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        # Inicializace kamery
        self.camera = Camera(width, height)
        self.width, self.height = width, height

        # Definice dostupných typů stromů
        self.tree_types = [TreeType1(), TreeType2()]
        
        # Renderer pro vykreslování
        self.renderer = Renderer(self.ctx, self.camera)
        
        # Generování L-systému a stromu
        self.generate_tree()

    def generate_tree(self):
        # Náhodně vybere typ stromu
        tree_type = random.choice(self.tree_types)
        print(f"Generuji strom typu: {tree_type.name}")
        
        # Vytvoří L-systém s vybraným typem
        self.l_system = LSystem(tree_type)
        
        # Generuje řetězec L-systému
        self.l_system.generate()
        
        # Vytvoří geometrii stromu
        vertices, indices = self.l_system.create_geometry()
        
        # Aktualizuje geometrii v rendereru
        self.renderer.update_geometry(vertices, indices)

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        
        # Generování nového stromu na stisk mezerníku
        if key == glfw.KEY_SPACE and action == glfw.PRESS:
            self.generate_tree()

    def resize_callback(self, window, width, height):
        self.width, self.height = width, height
        self.ctx.viewport = (0, 0, width, height)
        self.camera.set_projection(width, height)

    def run(self):
        # Hlavní smyčka aplikace
        while not glfw.window_should_close(self.window):
            # Vyčištění obrazovky
            self.ctx.clear(0.2, 0.3, 0.3)
            
            # Vykreslení stromu
            self.renderer.render()
            
            # Výměna bufferů a zpracování událostí
            glfw.swap_buffers(self.window)
            glfw.poll_events()

        # Úklid
        self.renderer.cleanup()
        glfw.terminate()

def main():
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"Chyba: {e}")
        glfw.terminate()

if __name__ == "__main__":
    main()
