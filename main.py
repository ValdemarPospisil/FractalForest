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
from generation.forest import ForestGenerator  # Nový import pro generování lesa



def setup_logging():
    """Nastaví logging pro aplikaci."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s -  %(levelname)s - %(message)s', 
        handlers=[
            # logging.FileHandler("logs/app.log"), # Optional: log to file
            logging.StreamHandler()
        ]
    )
    logging.getLogger('OpenGL').setLevel(logging.WARNING) # Quieten ModernGL/OpenGL noise if needed
    logging.info("Logging system initialized")

def main():
    setup_logging()
    logger = logging.getLogger(__name__) # Use specific logger

    logger.info("Initializing application...")
    try:
        renderer = Renderer(width=1366, height=768, title="Procedural L-System Forest") # Larger window
        camera = Camera(renderer.width, renderer.height)

        # Nastavíme kameru trochu výš a dál, aby byla vidět i zem
        camera.position = np.array([0.0, 1.0, 4.0]) # Vyšší a dále
        camera.update_view_matrix()
        logger.info("Renderer and Camera initialized.")
        logger.info(f"Camera positioned at {camera.position}, looking at {camera.target}")
        
        # Vytvoříme širokou zem (velikost 30x30)
        renderer.create_ground(size=30.0, color=(0.6, 0.4, 0.2)) # Hnědá barva
        logger.info("Ground plane created")
    except Exception as e:
        logger.exception("Failed to initialize Renderer or Camera.")
        return # Exit if core components fail

    # Display available tree types
    available_trees = [tree_cls().name for tree_cls in TREE_TYPES]
    logger.info(f"Available tree types ({len(available_trees)}): {', '.join(available_trees)}")
    logger.info("Controls: ESC=Exit, SPACE=New Random Tree, 1-%d=Select Specific Tree, F=Generate Forest", len(TREE_TYPES))


    # Initial tree generation
    current_tree_def = None
    forest_generator = None
    forest_mode = False  # Nový příznak pro režim lesa
    forest_density = 0.5  # Výchozí hustota lesa
    forest_area_size = 20.0  # Výchozí velikost oblasti lesa
    
    def regenerate_tree(tree_definition, renderer):
        """Pomocná funkce pro regeneraci stromu."""
        nonlocal current_tree_def, forest_mode
        if tree_definition is None:
            logger.error("Cannot regenerate tree, definition is None.")
            return

        # Přepnutí do režimu jednoho stromu
        forest_mode = False
        
        # Vymazání všech stromů lesa
        if forest_generator and hasattr(forest_generator, 'trees'):
            for i in range(len(forest_generator.trees)):
                renderer.setup_object(np.array([]), np.array([]), np.array([]), object_id=f"tree_{i}")

        current_tree_def = tree_definition # Store current definition
        print("------------------------------------------------------------------------------------------------")
        print(" ")
        logger.info(f"Regenerating tree: {tree_definition.name}")
        try:
            lsystem = tree_definition.get_lsystem()
            iterations = tree_definition.get_iterations()
            lsystem.generate(iterations)

            logger.info(f"L-System params - Angle: {math.degrees(lsystem.angle):.1f}°, Scale: {lsystem.scale:.2f}, Width: {lsystem.initial_width:.3f}")
            logger.info(f"Generated string length: {len(lsystem.current_string)} characters")

            vertices, colors, normals = lsystem.get_vertices()

            if vertices.size > 0:
                # Použijeme ID "tree" pro oddělení stromu od země
                renderer.setup_object(vertices, colors, normals, object_id="tree") # Pass normals too
                logger.info(f"Generated {vertices.size // 3} vertices for rendering")
            else:
                logger.error("No vertices generated during regeneration.")
                renderer.setup_object(np.array([]), np.array([]), np.array([]), object_id="tree") # Clear geometry

        except Exception as e:
            logger.exception(f"Error regenerating tree '{tree_definition.name}': {e}")
            renderer.setup_object(np.array([]), np.array([]), np.array([]), object_id="tree") # Clear on error

    def generate_forest():
        """Pomocná funkce pro generování lesa."""
        nonlocal forest_generator, forest_mode, current_tree_def
        
        # Přepnutí do režimu lesa
        forest_mode = True
        
        # Vymazání strom v režimu jednoho stromu
        renderer.setup_object(np.array([]), np.array([]), np.array([]), object_id="tree")
        current_tree_def = None
        
        print("------------------------------------------------------------------------------------------------")
        print(" ")
        logger.info(f"Generating forest with density {forest_density:.2f} in area size {forest_area_size:.1f}")
        
        try:
            # Vytvoříme generátor lesa, pokud ještě není
            if forest_generator is None:
                forest_generator = ForestGenerator(
                    renderer,
                    area_size=forest_area_size,
                    density=forest_density,
                    min_trees=15,
                    max_trees=35,
                    min_distance=1.0
                )
            else:
                # Aktualizace parametrů
                forest_generator.area_size = forest_area_size
                forest_generator.density = forest_density
            
            # Generování a vykreslení lesa
            forest_generator.generate_forest()
            forest_generator.render_forest()
            
            # Získání informace o vygenerovaném lese
            if hasattr(forest_generator, 'trees'):
                tree_types = [t[0].name for t in forest_generator.trees]
                type_counts = {}
                for t in tree_types:
                    if t in type_counts:
                        type_counts[t] += 1
                    else:
                        type_counts[t] = 1
                
                logger.info(f"Generated forest with {len(forest_generator.trees)} trees:")
                for tree_type, count in type_counts.items():
                    logger.info(f"  - {tree_type}: {count} trees")
            
        except Exception as e:
            logger.exception(f"Error generating forest: {e}")


    # Generate the first tree
    regenerate_tree(get_random_tree_type(), renderer)


    logger.info("Starting main loop...")
    last_time = glfw.get_time()
    angle_y = 0.0
    angle_x = 0.0 # Start without tilt
    
    # Pro ovládání hustoty lesa a velikosti oblasti
    forest_density_changing = False
    forest_area_changing = False
    key_f_last_state = glfw.RELEASE

    while not renderer.should_close():
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time

        # Slow rotation - pouze pro jeden strom
        if not forest_mode:
            angle_y += 0.15 * delta_time # Slower rotation

        model_matrix = Matrix44.from_y_rotation(angle_y) * Matrix44.from_x_rotation(angle_x)

        try:
            renderer.render(camera, model_matrix)
            renderer.swap_buffers()
        except Exception as e:
             logger.exception("Error during rendering loop.")
             # Decide if error is fatal or can be skipped
             # glfw.set_window_should_close(renderer.window, True) # Example: Exit on render error

        renderer.poll_events() # Process input events

        # --- Input Handling ---
        if glfw.get_key(renderer.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            logger.info("ESC pressed, exiting.")
            glfw.set_window_should_close(renderer.window, True)

        # Regenerate random tree
        if glfw.get_key(renderer.window, glfw.KEY_SPACE) == glfw.PRESS:
             # Simple debounce: check if tree def changed recently? Or just allow rapid fire.
             # For now, allow rapid fire.
             regenerate_tree(get_random_tree_type(), renderer)
             # Reset rotation? Optional. angle_y = 0.0

        # Select specific tree type (adjust range based on actual number of TREE_TYPES)
        num_tree_types = len(TREE_TYPES)
        for i in range(num_tree_types):
            key = glfw.KEY_1 + i
            if key <= glfw.KEY_9: # Check keys 1 through 9
                 if glfw.get_key(renderer.window, key) == glfw.PRESS:
                     selected_tree_def = TREE_TYPES[i]()
                     # Regenerate only if the type is different from the current one
                     if current_tree_def is None or selected_tree_def.name != current_tree_def.name:
                         regenerate_tree(selected_tree_def, renderer)
                         # angle_y = 0.0 # Reset rotation on type change
                     break # Exit loop once a key is pressed

        # --- Nové ovládání pro generování lesa ---
        # Generování lesa po stisknutí F
        key_f_current_state = glfw.get_key(renderer.window, glfw.KEY_F)
        if key_f_current_state == glfw.PRESS and key_f_last_state == glfw.RELEASE:
            generate_forest()
        key_f_last_state = key_f_current_state
        
        # Ovládání hustoty lesa
        if glfw.get_key(renderer.window, glfw.KEY_LEFT_BRACKET) == glfw.PRESS:  # [ pro snížení hustoty
            forest_density = max(0.1, forest_density - 0.05)
            forest_density_changing = True
            logger.debug(f"Forest density decreased to {forest_density:.2f}")
        elif glfw.get_key(renderer.window, glfw.KEY_RIGHT_BRACKET) == glfw.PRESS:  # ] pro zvýšení hustoty
            forest_density = min(1.0, forest_density + 0.05)
            forest_density_changing = True
            logger.debug(f"Forest density increased to {forest_density:.2f}")
        elif forest_density_changing:
            forest_density_changing = False
            logger.info(f"Forest density set to {forest_density:.2f}")
            if forest_mode:
                generate_forest()  # Regenerovat les s novou hustotou
        
        # Ovládání velikosti oblasti lesa
        if glfw.get_key(renderer.window, glfw.KEY_MINUS) == glfw.PRESS:  # - pro zmenšení oblasti
            forest_area_size = max(10.0, forest_area_size - 1.0)
            forest_area_changing = True
            logger.debug(f"Forest area decreased to {forest_area_size:.1f}")
        elif glfw.get_key(renderer.window, glfw.KEY_EQUAL) == glfw.PRESS:  # = pro zvětšení oblasti
            forest_area_size = min(40.0, forest_area_size + 1.0)
            forest_area_changing = True
            logger.debug(f"Forest area increased to {forest_area_size:.1f}")
        elif forest_area_changing:
            forest_area_changing = False
            logger.info(f"Forest area size set to {forest_area_size:.1f}")
            if forest_mode:
                generate_forest()  # Regenerovat les s novou velikostí oblasti
        
        # Ovládání kamery s novým systémem pohybu
        move_speed = 1 * delta_time
        camera_moved = False
        
        # Pohyb dopředu/dozadu - posun kamery a cíl stejným směrem
        if glfw.get_key(renderer.window, glfw.KEY_W) == glfw.PRESS:
            camera.move(camera.front, move_speed)
            camera_moved = True
        if glfw.get_key(renderer.window, glfw.KEY_S) == glfw.PRESS:
            camera.move(camera.back, move_speed)
            camera_moved = True
            
        # Pohyb doleva/doprava - posun kamery a cíl stejným směrem
        if glfw.get_key(renderer.window, glfw.KEY_A) == glfw.PRESS:
            camera.move(camera.left, move_speed)
            camera_moved = True
        if glfw.get_key(renderer.window, glfw.KEY_D) == glfw.PRESS:
            camera.move(camera.right, move_speed)
            camera_moved = True
            
        # Pohyb nahoru/dolů - posun kamery a cíl stejným směrem
        if glfw.get_key(renderer.window, glfw.KEY_Q) == glfw.PRESS:
            camera.move(camera.down, move_speed)
            camera_moved = True
        if glfw.get_key(renderer.window, glfw.KEY_E) == glfw.PRESS:
            camera.move(camera.up, move_speed)
            camera_moved = True
            
        # Pokud se pohybovala kamera, aktualizujeme view matici
        if camera_moved:
            camera.update_view_matrix()
            logger.debug(f"Camera moved to position {camera.position}, looking at {camera.target}")

    logger.info("Cleaning up resources...")
    renderer.cleanup()
    glfw.terminate()
    logger.info("Application exited cleanly.")

if __name__ == "__main__":
    main()
