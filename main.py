# main.py
import glfw
from pyrr import Matrix44
import math
import random

# Importy z našich modulů
from engine.renderer import Renderer
from engine.camera import Camera
from generation.tree import get_random_tree_type

def main():
    print("Initializing...")
    # Vytvoření instance renderu (inicializuje okno a ModernGL)
    renderer = Renderer(width=1024, height=768, title="Náhodný L-System Strom")

    # Vytvoření instance kamery
    camera = Camera(renderer.width, renderer.height)
    # Můžeme kameru trochu posunout pro lepší výchozí pohled
    camera.position.z = 4.0
    camera.position.y = 0.5
    camera.update_view_matrix()

    print("Generating tree...")
    # Získání náhodného typu stromu
    tree_definition = get_random_tree_type()

    # Získání L-systému pro tento typ
    lsystem = tree_definition.get_lsystem()

    # Generování řetězce L-systému
    iterations = tree_definition.get_iterations()
    lsystem.generate(iterations)
    print(f"Generated L-system string with {iterations} iterations (length: {len(lsystem.current_string)})")

    # Získání vrcholů a barev
    vertices, colors = lsystem.get_vertices()

    if vertices.size == 0:
        print("Error: No vertices generated. Exiting.")
        renderer.cleanup()
        glfw.terminate()
        return

    print(f"Generated {vertices.size // 3} vertices.")

    # Předání geometrie rendereru k vytvoření VBO/VAO
    renderer.setup_object(vertices, colors)

    print("Starting main loop...")
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

            
        if glfw.get_key(renderer.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(renderer.window, True)

        # Možnost znovu vygenerovat strom po stisku klávesy (např. R)
        if glfw.get_key(renderer.window, glfw.KEY_SPACE) == glfw.PRESS:
            print("\nRegenerating tree...")
            tree_definition = get_random_tree_type()
            lsystem = tree_definition.get_lsystem()
            iterations = tree_definition.get_iterations()
            lsystem.generate(iterations)
            print(f"Generated L-system string with {iterations} iterations (length: {len(lsystem.current_string)})")
            vertices, colors = lsystem.get_vertices()
            if vertices.size > 0:
                 renderer.setup_object(vertices, colors)
                 print(f"Generated {vertices.size // 3} vertices.")
            else:
                 print("Error: No vertices generated during regeneration.")
                 renderer.setup_object(np.array([]), np.array([])) # Vyčistí VAO

    print("Cleaning up...")
    # Úklid po skončení smyčky
    renderer.cleanup()

    # Ukončení GLFW
    glfw.terminate()
    print("Exited cleanly.")

if __name__ == "__main__":
    main()
