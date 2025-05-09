import glfw
import pyrr
from pyrr import Matrix44
import math
import dearpygui.dearpygui as dpg
import logging
import os
import numpy as np

# Importy z našich modulů
from engine.renderer import Renderer 
from engine.camera import Camera    
from generation.tree import get_random_tree_type, TREE_TYPES
from generation.forest import ForestGenerator
from ui import UIManager  



def setup_logging():
    """Nastaví logging pro aplikaci."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s -  %(levelname)s - %(message)s', 
        handlers=[
            # logging.FileHandler("logs/app.log"), 
            logging.StreamHandler()
        ]
    )
    logging.getLogger('OpenGL').setLevel(logging.WARNING) 
    logging.info("Logging system initialized")

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Initializing application...")
    try:
        dpg.create_context()
        dpg.create_viewport(title='Procedural L-System Forest', width=1366, height=768)
        renderer = Renderer(width=1366, height=768, title="Procedural L-System Forest")
        camera = Camera(renderer.width, renderer.height)

        camera.position = np.array([0.0, 1.0, 4.0])
        camera.update_view_matrix()
        logger.info("Renderer and Camera initialized.")
        logger.info(f"Camera positioned at {camera.position}, looking at {camera.target}")
        
        # Vytvoříme širokou zem (velikost 30x30)
        renderer.create_ground(size=60.0, color=(0.267, 0.467, 0.2))
        logger.info("Ground plane created")
        
        # Inicializace UI manažera
        ui_manager = UIManager(renderer.ctx, (renderer.width, renderer.height))
        logger.info("UI Manager initialized")
    except Exception as e:
        logger.exception("Failed to initialize Renderer or Camera.")
        return

    available_trees = [tree_cls().name for tree_cls in TREE_TYPES]
    logger.info(f"Available tree types ({len(available_trees)}): {', '.join(available_trees)}")
    logger.info("Controls: ESC=Exit, SPACE=New Random Tree, 1-%d=Select Specific Tree, F=Generate Forest", len(TREE_TYPES))
    logger.info("Camera controls: WASD=Move, QE=Up/Down, Right Mouse Button=Look around")


    # Initial tree generation
    current_tree_def = None
    forest_generator = None
    forest_mode = False  # Nový příznak pro režim lesa
    min_distance = 0.5  # Výchozí hustota lesa
    forest_area_size = 20.0  # Výchozí velikost oblasti lesa
    tree_count = 45

    
    def regenerate_tree(tree_definition, renderer):
        """Pomocná funkce pro regeneraci stromu."""
        nonlocal current_tree_def, forest_mode
        if tree_definition is None:
            logger.error("Cannot regenerate tree, definition is None.")
            return

        # Přepnutí do režimu jednoho stromu
        forest_mode = False
        
        # Aktualizace UI manažera
        ui_manager.set_forest_mode(False)
        ui_manager.set_current_tree(tree_definition.name)
        
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
        
        # Aktualizace UI manažera
        ui_manager.set_forest_mode(True)
        
        # Vymazání strom v režimu jednoho stromu
        renderer.setup_object(np.array([]), np.array([]), np.array([]), object_id="tree")
        current_tree_def = None
        
        print("------------------------------------------------------------------------------------------------")
        print(" ")
        logger.info(f"Generating forest with min distance  {min_distance:.2f} in area size {forest_area_size:.1f}")
        
        try:
            # Vytvoříme generátor lesa, pokud ještě není
            if forest_generator is None:
                forest_generator = ForestGenerator(
                    renderer,
                    area_size=forest_area_size,
                    min_distance=min_distance,
                    tree_count=tree_count,
                )
            else:
                # Aktualizace parametrů
                forest_generator.area_size = forest_area_size
                forest_generator.min_distance = min_distance 
                forest_generator.tree_count = tree_count
            
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
                
                # Aktualizace informací v UI manažeru
                ui_manager.set_forest_info(len(forest_generator.trees), type_counts)
                
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
    min_distance_changing = False
    forest_area_changing = False
    tree_count_changing = False
    key_f_last_state = glfw.RELEASE
    
    # Proměnné pro ovládání kamery myší
    mouse_look_enabled = False
    last_mouse_x, last_mouse_y = 0.0, 0.0
    mouse_sensitivity = 0.003  # Citlivost myši pro otáčení kamery
    
    # Proměnné pro výpočet FPS
    frame_count = 0
    fps_update_time = last_time
    current_fps = 0.0
    
    # Callbacky pro myš
    def mouse_button_callback(window, button, action, mods):
        nonlocal mouse_look_enabled, last_mouse_x, last_mouse_y # Přidej last_mouse_x, last_mouse_y, pokud je nastavuješ zde
        
        if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS: # Reaguj pouze na stisk
            mouse_look_enabled = not mouse_look_enabled # Přepni stav

            if mouse_look_enabled:
                # Zapnutí režimu ovládání kamery myší
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                # Získat aktuální pozici myši jako výchozí bod
                # Je důležité to udělat ZDE, aby nedocházelo ke skokům kamery při aktivaci
                x, y = glfw.get_cursor_pos(window)
                last_mouse_x, last_mouse_y = x, y
                logger.debug("Mouse look enabled")
            else:
                # Vypnutí režimu ovládání kamery myší
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                logger.debug("Mouse look disabled")
    
    def cursor_position_callback(window, x_pos, y_pos):
        nonlocal last_mouse_x, last_mouse_y, camera
        
        if mouse_look_enabled:
            # Výpočet změny pozice myši
            x_offset = x_pos - last_mouse_x
            y_offset = last_mouse_y - y_pos  # Převráceno (y-osa jde odshora dolů)
            
            last_mouse_x = x_pos
            last_mouse_y = y_pos
            
            # Aplikace změny na směr kamery
            x_offset *= mouse_sensitivity
            y_offset *= mouse_sensitivity
            
            # 1. Yaw rotace (kolem osy Y)
            yaw_matrix = pyrr.Matrix44.from_y_rotation(x_offset) # Rotace kolem globální Y
            
            current_direction = np.array(camera.direction, dtype=np.float32)
            if current_direction.shape != (3,): # Kontrola
                logger.error(f"Initial camera.direction has unexpected shape: {current_direction.shape}")
                return
            
            # Převod na 4D vektor, zajisti float32 pro konzistenci
            direction_4d = np.append(current_direction, 0.0).astype(np.float32)

            # --- ZMĚNA ZDE ---
            # Použij pyrr.matrix44.apply_to_vector pro transformaci vektoru
            # nebo operátor @
            # Varianta A: apply_to_vector
            transformed_vec4 = pyrr.matrix44.apply_to_vector(yaw_matrix, direction_4d)
            # Varianta B: operátor @ (vyzkoušej, pokud A nefunguje, nebo preferuješ kratší zápis)
            # transformed_vec4 = yaw_matrix @ direction_4d
            
            # Logování pro ověření výsledku transformace
            logger.debug(f"direction_4d (input to transform): {direction_4d}, shape: {np.shape(direction_4d)}, dtype: {direction_4d.dtype}")
            logger.debug(f"transformed_vec4 (after transform): {transformed_vec4}, type: {type(transformed_vec4)}, shape: {np.shape(transformed_vec4)}")

            # Získání prvních tří komponent a explicitní konverze na numpy array
            # Pokud transformed_vec4 je již np.array, np.array() vytvoří kopii.
            rotated_yaw_direction_3d = np.array(transformed_vec4[:3], dtype=np.float32)

            logger.debug(f"rotated_yaw_direction_3d (before norm): {rotated_yaw_direction_3d}, type: {type(rotated_yaw_direction_3d)}, shape: {np.shape(rotated_yaw_direction_3d)}")

            norm_yaw = np.linalg.norm(rotated_yaw_direction_3d)
            if norm_yaw > 0.0001:
                rotated_yaw_direction_3d /= norm_yaw
            else:
                logger.warning("Yaw rotation resulted in a near-zero vector.")
                return

            # 2. Pitch rotace (kolem pravé osy kamery)
            world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
            
            # Logování těsně před np.cross
            logger.debug(f"rotated_yaw_direction_3d (final for cross): {rotated_yaw_direction_3d}, shape: {np.shape(rotated_yaw_direction_3d)}, dtype: {rotated_yaw_direction_3d.dtype}")
            logger.debug(f"world_up (final for cross): {world_up}, shape: {np.shape(world_up)}, dtype: {world_up.dtype}")

            right_vector = np.cross(rotated_yaw_direction_3d, world_up)
            norm_right = np.linalg.norm(right_vector)
            if norm_right > 0.0001:
                right_vector /= norm_right
            else:
                if np.allclose(rotated_yaw_direction_3d, world_up):
                    right_vector = np.array([1.0, 0.0, 0.0], dtype=np.float32)
                elif np.allclose(rotated_yaw_direction_3d, -world_up):
                    right_vector = np.array([-1.0, 0.0, 0.0], dtype=np.float32)
                else: 
                    logger.warning("Could not determine a valid right_vector for pitch (rotated_yaw_direction_3d may be zero or colinear with world_up in an unexpected way). Using fallback.")
                    # Fallback na křížový součin s jinou osou, pokud je rotated_yaw_direction_3d např. [0,0,1]
                    if abs(rotated_yaw_direction_3d[1]) < 0.99: # Není skoro vertikální
                        right_vector = np.cross(rotated_yaw_direction_3d, np.array([0.0, 1.0, 0.0], dtype=np.float32)) # Zkus znovu s world_up
                        if np.linalg.norm(right_vector) < 0.0001: # Pokud stále problém
                             right_vector = np.array([1.0, 0.0, 0.0], dtype=np.float32) # Absolutní fallback
                    else: # Je skoro vertikální
                        right_vector = np.array([1.0, 0.0, 0.0], dtype=np.float32)

                    # Normalizuj fallback right_vector, pokud byl vypočítán přes cross
                    if np.linalg.norm(right_vector) > 0.0001:
                        right_vector /= np.linalg.norm(right_vector)
                    else: # Pokud i fallback je nulový (nemělo by nastat s [1,0,0])
                         right_vector = np.array([1.0, 0.0, 0.0], dtype=np.float32) # Jistota


            # Vytvoříme rotační matici kolem pravé osy
            # OPRAVA ZDE: Použij 'right_vector'
            pitch_matrix = pyrr.Matrix44(pyrr.matrix44.create_from_axis_rotation(right_vector, y_offset))
            
            # Aplikujeme pitch rotaci na rotated_yaw_direction_3d
            # Nejprve převedeme rotated_yaw_direction_3d na 4D pro transformaci
            direction_to_pitch_4d = np.append(rotated_yaw_direction_3d, 0.0).astype(np.float32)
            
            # Varianta A: apply_to_vector
            final_rotated_vec4 = pyrr.matrix44.apply_to_vector(pitch_matrix, direction_to_pitch_4d)
            # Varianta B: operátor @
            # final_rotated_vec4 = pitch_matrix @ direction_to_pitch_4d
            
            final_direction_3d = np.array(final_rotated_vec4[:3], dtype=np.float32)
            
            # Normalizace finálního směrového vektoru
            norm_final = np.linalg.norm(final_direction_3d)
            if norm_final > 0.0001:
                final_direction_3d /= norm_final
            else:
                logger.warning("Pitch rotation resulted in a near-zero final direction.")
                return 
            
            # Omezení úhlu pitch
            if final_direction_3d[1] > 0.995: final_direction_3d[1] = 0.995
            if final_direction_3d[1] < -0.995: final_direction_3d[1] = -0.995
            final_direction_3d /= np.linalg.norm(final_direction_3d) # Znovu normalizovat po omezení

            # Aktualizace cílového bodu kamery
            camera.target = np.array(camera.position, dtype=np.float32) + final_direction_3d
            camera.update_view_matrix()


    # Nastavení callbacků
    glfw.set_mouse_button_callback(renderer.window, mouse_button_callback)
    glfw.set_cursor_pos_callback(renderer.window, cursor_position_callback)

    # Callback pro přepínání viditelnosti UI
    key_h_last_state = glfw.RELEASE
    
    while not renderer.should_close():
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Výpočet FPS
        frame_count += 1
        if current_time - fps_update_time >= 0.5:  # Aktualizace každou půl sekundu
            current_fps = frame_count / (current_time - fps_update_time)
            fps_update_time = current_time
            frame_count = 0

        # Slow rotation - pouze pro jeden strom, a jen když není aktivní ovládání kamery myší
        if not forest_mode and not mouse_look_enabled:
            angle_y += 0.15 * delta_time # Slower rotation

        model_matrix = Matrix44.from_y_rotation(angle_y) * Matrix44.from_x_rotation(angle_x)

        try:
            # Vykreslení scény
            renderer.render(camera, model_matrix)
            
            # Vykreslení UI
            ui_manager.render(fps=current_fps)
            
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

        # Toggles pro UI
        key_h_current_state = glfw.get_key(renderer.window, glfw.KEY_H)
        if key_h_current_state == glfw.PRESS and key_h_last_state == glfw.RELEASE:
            ui_manager.toggle_controls_visibility()
            logger.debug("Toggled controls visibility")
        key_h_last_state = key_h_current_state
        
        # Toggle FPS viditelnosti
        key_p_last_state = glfw.RELEASE
        key_p_current_state = glfw.get_key(renderer.window, glfw.KEY_P)
        if key_p_current_state == glfw.PRESS and key_p_last_state == glfw.RELEASE:
            ui_manager.toggle_fps_visibility()
            logger.debug("Toggled FPS visibility")
        key_p_last_state = key_p_current_state

        # Regenerate random tree
        if glfw.get_key(renderer.window, glfw.KEY_G) == glfw.PRESS:
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
                         angle_y = 0.0 # Reset rotation on type change
                     break # Exit loop once a key is pressed

        # --- Nové ovládání pro generování lesa ---
        # Generování lesa po stisknutí F
        key_f_current_state = glfw.get_key(renderer.window, glfw.KEY_F)
        if key_f_current_state == glfw.PRESS and key_f_last_state == glfw.RELEASE:
            generate_forest()
        key_f_last_state = key_f_current_state
        
        # Ovládání hustoty lesa
        if glfw.get_key(renderer.window, glfw.KEY_N) == glfw.PRESS:
            min_distance = max(0.1, min_distance - 0.01)
            min_distance_changing = True
            logger.debug(f"Min distance between trees decreased to {min_distance:.2f}")
        elif glfw.get_key(renderer.window, glfw.KEY_M) == glfw.PRESS:
            min_distance = min(1.0, min_distance + 0.01)
            min_distance_changing = True
            logger.debug(f"Min distance between trees increased to {min_distance:.2f}")
        elif min_distance_changing:
            min_distance_changing = False
            logger.info(f"Min distance between trees set to {min_distance:.2f}")
            if forest_mode:
                generate_forest()
        
        # Ovládání velikosti oblasti lesa
        if glfw.get_key(renderer.window, glfw.KEY_K) == glfw.PRESS:
            forest_area_size = max(5.0, forest_area_size - 0.5)
            forest_area_changing = True
            logger.debug(f"Forest area decreased to {forest_area_size:.1f}")
        elif glfw.get_key(renderer.window, glfw.KEY_L) == glfw.PRESS:
            forest_area_size = min(60.0, forest_area_size + 0.5)
            forest_area_changing = True
            logger.debug(f"Forest area increased to {forest_area_size}")
        elif forest_area_changing:
            forest_area_changing = False
            logger.info(f"Forest area size set to {forest_area_size:.1f}")
            if forest_mode:
                generate_forest()

        # Ovládání počtu stromů v lese      
        if glfw.get_key(renderer.window, glfw.KEY_O) == glfw.PRESS:
            tree_count = max(5, tree_count - 1)
            tree_count_changing = True
            logger.debug(f"Forest tree count decreased to {tree_count}")
        elif glfw.get_key(renderer.window, glfw.KEY_P) == glfw.PRESS:
            tree_count = min(200, tree_count + 1)
            tree_count_changing = True
            logger.debug(f"Forest tree count increased to {tree_count}")
        elif tree_count_changing:
            tree_count_changing = False
            logger.info(f"Forest tree count set to {tree_count}")
            if forest_mode:
                generate_forest()
        
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
        if glfw.get_key(renderer.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS or glfw.get_key(renderer.window, glfw.KEY_Q) == glfw.PRESS :
            camera.move(camera.down, move_speed)
            camera_moved = True
        if glfw.get_key(renderer.window, glfw.KEY_SPACE) == glfw.PRESS or glfw.get_key(renderer.window, glfw.KEY_E) == glfw.PRESS:
            camera.move(camera.up, move_speed)
            camera_moved = True
            
        # Pokud se pohybovala kamera, aktualizujeme view matici
        if camera_moved:
            camera.update_view_matrix()
            logger.debug(f"Camera moved to position {camera.position}, looking at {camera.target}")

    logger.info("Cleaning up resources...")
    renderer.cleanup()
    if 'ui_manager' in locals():
        ui_manager.cleanup()
    glfw.terminate()
    if dpg.is_dearpygui_running():
        dpg.destroy_context()
    logger.info("Application exited cleanly.")

if __name__ == "__main__":
    main()
