import glfw
from pyrr import Matrix44
import math
import random
import logging
import os
import numpy as np

# Importy z našich modulů
from engine.renderer import Renderer
from engine.camera import Camera
from generation.tree import get_random_tree_type

def setup_logging():
    """Nastaví logging pro aplikaci."""
    # Zajistíme, že existuje adresář pro logy
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Nastavení formátu a úrovně loggeru
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/lsystem_tree.log'),
            logging.StreamHandler()  # Výstup i do konzole
        ]
    )
    logging.info("Logging system initialized")

def main():
    # Nastavení loggování
    setup_logging()
    
    logging.info("Initializing application...")
    # Vytvoření instance renderu (inicializuje okno a ModernGL)
    renderer = Renderer(width=1024, height=768, title="Náhodný L-System Strom")

    # Vytvoření instance kamery
    camera = Camera(renderer.width, renderer.height)
    # Lepší pozice kamery pro pohled na strom
    camera.position = np.array([0.0, 0.5, 3.0])  # Posunuta dozadu a mírně nahoru
    camera.target = np.array([0.0, 0.0, 0.0])    # Míří na střed
    camera.update_view_matrix()
    logging.info("Camera positioned at %s, looking at %s", camera.position, camera.target)

    logging.info("Generating tree...")
    # Získání náhodného typu stromu
    tree_definition = get_random_tree_type()

    # Získání L-systému pro tento typ
    lsystem = tree_definition.get_lsystem()

    # Generování řetězce L-systému
    iterations = tree_definition.get_iterations()
    lsystem.generate(iterations)
    logging.info(f"Generated L-system string with {iterations} iterations (length: {len(lsystem.current_string)})")

    # Získání vrcholů a barev
    vertices, colors = lsystem.get_vertices()

    if vertices.size == 0:
        logging.error("No vertices generated. Exiting.")
        renderer.cleanup()
        glfw.terminate()
        return

    logging.info(f"Generated {vertices.size // 3} vertices.")

    # Předání geometrie rendereru k vytvoření VBO/VAO
    renderer.setup_object(vertices, colors)

    logging.info("Starting main loop...")
    # Hlavní smyčka
    last_time = glfw.get_time()
    angle_y = 0.0
    angle_x = math.radians(10) # Mírný náklon na začátku

    while not renderer.should_close():
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time

        # Pomalé otáčení stromu pro ukázku
        angle_y += 0.3 * delta_time # Rychlost otáčení

        # Výpočet modelové matice (otáčení)
        model_matrix = Matrix44.from_y_rotation(angle_y) * Matrix44.from_x_rotation(angle_x)

        # Vykreslení scény
        renderer.render(camera, model_matrix)

        # Výměna bufferů a zpracování událostí
        renderer.swap_buffers()
        renderer.poll_events()

        # Klávesové zkratky
        if glfw.get_key(renderer.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            logging.info("ESC pressed, exiting...")
            glfw.set_window_should_close(renderer.window, True)

        # Možnost znovu vygenerovat strom po stisku klávesy (mezerník)
        if glfw.get_key(renderer.window, glfw.KEY_SPACE) == glfw.PRESS:
            logging.info("Regenerating tree...")
            tree_definition = get_random_tree_type()
            lsystem = tree_definition.get_lsystem()
            iterations = tree_definition.get_iterations()
            lsystem.generate(iterations)
            logging.info(f"Generated L-system string with {iterations} iterations (length: {len(lsystem.current_string)})")
            vertices, colors = lsystem.get_vertices()
            if vertices.size > 0:
                 renderer.setup_object(vertices, colors)
                 logging.info(f"Generated {vertices.size // 3} vertices.")
            else:
                 logging.error("No vertices generated during regeneration.")
                 renderer.setup_object(np.array([]), np.array([])) # Vyčistí VAO

    logging.info("Cleaning up...")
    # Úklid po skončení smyčky
    renderer.cleanup()

    # Ukončení GLFW
    glfw.terminate()
    logging.info("Application exited cleanly.")

if __name__ == "__main__":
    main()
