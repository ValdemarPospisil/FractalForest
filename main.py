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
from generation.tree import get_random_tree_type, get_tree_by_name, TREE_TYPES

def setup_logging():
    """Nastaví logging pro aplikaci."""
    # Zajistíme, že existuje adresář pro logy
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Nastavení formátu a úrovně loggeru
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
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
    camera.position = np.array([0.0, 0.25, 2.0])  # Posunuta dozadu a mírně nahoru
    camera.target = np.array([0.2, 0.25, 0.0])    # Míří na střed
    camera.update_view_matrix()
    logging.info("Camera positioned at %s, looking at %s", camera.position, camera.target)

    # Vypsání dostupných typů stromů
    available_trees = [tree_cls().name for tree_cls in TREE_TYPES]
    logging.info(f"Available tree types: {', '.join(available_trees)}")

    logging.info("Generating tree...")
    # Získání náhodného typu stromu
    tree_definition = get_random_tree_type()
    logging.info(f"Selected tree type: '{tree_definition.name}'")

    # Získání L-systému pro tento typ
    lsystem = tree_definition.get_lsystem()

    # Generování řetězce L-systému
    iterations = tree_definition.get_iterations()
    lsystem.generate(iterations)
    logging.info(f"Generated L-system with {iterations} iterations")
    logging.info(f"Base parameters - angle: {math.degrees(lsystem.angle):.1f}°, scale: {lsystem.scale:.2f}")
    logging.info(f"String length: {len(lsystem.current_string)} characters")

    # Získání vrcholů a barev
    vertices, colors, normals = lsystem.get_vertices()

    if vertices.size == 0:
        logging.error("No vertices generated. Exiting.")
        renderer.cleanup()
        glfw.terminate()
        return

    logging.info(f"Generated {vertices.size // 3} vertices for rendering")

    # Předání geometrie rendereru k vytvoření VBO/VAO
    renderer.setup_object(vertices, colors)

    # Výpis informací o používaných klávesách
    logging.info("Controls: ESC - Exit, SPACE - Generate new tree, 1-6 - Select specific tree type")
    
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
            logging.info("Regenerating random tree...")
            tree_definition = get_random_tree_type()
            regenerate_tree(tree_definition, renderer)

        # Výběr konkrétního typu stromu klávesami 1-6
        for i in range(6):
            if glfw.get_key(renderer.window, glfw.KEY_1 + i) == glfw.PRESS and i < len(TREE_TYPES):
                tree_class = TREE_TYPES[i]
                tree_definition = tree_class()
                logging.info(f"Selected specific tree type: '{tree_definition.name}'")
                regenerate_tree(tree_definition, renderer)
                break

    logging.info("Cleaning up...")
    # Úklid po skončení smyčky
    renderer.cleanup()

    # Ukončení GLFW
    glfw.terminate()
    logging.info("Application exited cleanly.")


def regenerate_tree(tree_definition, renderer):
    """Pomocná funkce pro regeneraci stromu."""
    lsystem = tree_definition.get_lsystem()
    iterations = tree_definition.get_iterations()
    lsystem.generate(iterations)
    
    logging.info(f"Generated L-system with {iterations} iterations")
    logging.info(f"Parameters - angle: {math.degrees(lsystem.angle):.1f}°, scale: {lsystem.scale:.2f}")
    logging.info(f"String length: {len(lsystem.current_string)} characters")
    
    # Nově předáváme normály do setup_object
    vertices, colors, normals = lsystem.get_vertices()
    if vertices.size > 0:
        renderer.setup_object(vertices, colors, normals)
        logging.info(f"Generated {vertices.size // 3} vertices for rendering")
    else:
        logging.error("No vertices generated during regeneration.")
        renderer.setup_object(np.array([]), np.array([]), np.array([])) # Vyčistí VAO

if __name__ == "__main__":
    main()
