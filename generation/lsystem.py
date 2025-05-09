import math
import random
import numpy as np
import logging

class LSystem:
    """Třída pro implementaci L-systému a generování geometrie."""
    def __init__(self, axiom, rules, angle, scale=0.8, initial_length=0.1, initial_width=0.05, # Default width increased
                 trunk_color=(0.55, 0.27, 0.07), leaf_color=(0.0, 0.8, 0.0)):
        self.axiom = axiom
        self.rules = rules
        self.angle = angle + random.uniform(-math.radians(1.5), math.radians(1.5)) # Slightly less random angle variation
        self.scale = scale * random.uniform(0.98, 1.02) # Less scale variation
        self.initial_length = initial_length
        self.initial_width = initial_width # Store initial width
        self.trunk_color = np.array(trunk_color, dtype='f4')

        # Leaf color handling (including ranges)
        if isinstance(leaf_color, list) and len(leaf_color) == 2:
             # Pick a random color within the provided range [min_color, max_color]
            leaf_min, leaf_max = leaf_color
            self.leaf_color = np.array([
                random.uniform(leaf_min[0], leaf_max[0]),
                random.uniform(leaf_min[1], leaf_max[1]),
                random.uniform(leaf_min[2], leaf_max[2])
            ], dtype='f4')
        elif isinstance(leaf_color, tuple):
             # Add slight variation to a single base color
            r = max(0, min(1, leaf_color[0] + random.uniform(-0.05, 0.05)))
            g = max(0, min(1, leaf_color[1] + random.uniform(-0.05, 0.05)))
            b = max(0, min(1, leaf_color[2] + random.uniform(-0.05, 0.05)))
            self.leaf_color = np.array([r, g, b], dtype='f4')
        else:
             # Fallback if leaf_color format is unexpected
            logging.warning("Unexpected leaf_color format, using default green.")
            self.leaf_color = np.array([0.0, 0.8, 0.0], dtype='f4')


        self.current_string = axiom
        self.iterations = 0

        # Calculate width reduction factor per branch level
        # Aim to reach a minimum width (e.g., 10% of initial) over max expected depth
        max_expected_depth = 10 # Estimate max depth for width calculation
        min_width_ratio = 0.1
        # Geometric reduction: width_factor ^ max_depth = min_ratio
        # width_factor = min_ratio ^ (1 / max_depth)
        if self.initial_width > 0:
             # Avoid potential division by zero or log(0) if max_expected_depth is 1 or less
             if max_expected_depth > 1:
                 self.width_reduction_factor = min_width_ratio**(1.0 / (max_expected_depth -1))
             else:
                 self.width_reduction_factor = min_width_ratio # Reach min width immediately if depth is 1
        else:
             self.width_reduction_factor = 1.0 # No reduction if initial width is zero
        logging.debug(f"Width reduction factor per level: {self.width_reduction_factor:.3f}")


        logging.debug(f"LSystem initialized with angle={math.degrees(self.angle):.1f}°, scale={self.scale:.2f}, width={self.initial_width:.3f}")

    def generate(self, iterations):
        """Generuje řetězec L-systému po zadaný počet iterací."""
        self.iterations = iterations
        current = self.axiom
        logging.debug(f"Starting L-system generation with axiom: {self.axiom}")

        for i in range(iterations):
            next_gen = ""
            for char in current:
                # Apply stochastic rule with low probability for variation
                # if char == 'F' and random.random() < 0.02:
                #     variation = random.choice(["F", "FF", "F[+F]F", "F[-F]F"])
                #     next_gen += variation
                #     # logging.debug(f"Applied stochastic rule on F: {variation}") # Can be noisy
                # el
                if char in self.rules:
                    next_gen += self.rules[char]
                else:
                    next_gen += char
            current = next_gen
            # Limit string length to prevent excessive memory usage/performance issues
            max_string_length = 80000 # Adjust as needed
            if len(current) > max_string_length:
                logging.warning(f"L-system string length exceeded limit ({max_string_length}). Truncating.")
                current = current[:max_string_length]
                # Ensure string doesn't end mid-branch
                while '[' in current and current.count('[') > current.count(']'):
                     current = current.rsplit('[', 1)[0] # Remove last unclosed '['
                break # Stop further generation

            logging.debug(f"Generation {i+1} complete, string length: {len(current)}")

        self.current_string = current
        logging.info(f"L-system string generated, final length: {len(self.current_string)}")

        # Check for simplicity (e.g., straight line)
        if self._is_too_simple(self.current_string):
            logging.warning("Generated L-system appears too simple (likely straight line). Applying fix.")
            # If it's just 'F's, add some basic branching
            if '[' not in self.current_string and 'F' in self.current_string:
                 self.current_string = self.current_string.replace("FFF", "F[+F][-F]FF", 2) # Add branches early
            else: # Otherwise use the general complexity adder
                self.current_string = self._add_complexity(self.current_string)
            logging.info(f"Applied complexity fix, new length: {len(self.current_string)}")


        return self.current_string

    def _is_too_simple(self, string):
        """Detekuje příliš jednoduché stromy (nedostatek větvení -> rovná čára)."""
        # Consider simple if only contains 'F' and very few or no branch symbols
        f_count = string.count('F')
        branch_symbols = string.count('[') + string.count(']')
        rotation_symbols = string.count('+') + string.count('-') + string.count('&') + \
                           string.count('^') + string.count('\\') + string.count('/')

        # Simple if many F's but almost no branching/rotation or very short overall
        is_simple = (f_count > 10 and branch_symbols < 4 and rotation_symbols < 4) or (len(string) < 20 and f_count > 3)

        # Also check if the string consists *only* of 'F' (e.g. "FFFFFFF")
        if not is_simple and f_count > 5:
            non_f_chars = [c for c in string if c != 'F']
            if not non_f_chars: # Only 'F' characters exist
                is_simple = True

        return is_simple


    def _add_complexity(self, string):
        """Přidá komplexitu do příliš jednoduchého L-systému."""
        # Basic fix: find 'F's and add random branches after them
        result = ""
        branch_probability = 0.25 # Higher probability to ensure branching
        min_branches_to_add = 3
        branches_added = 0

        for i, char in enumerate(string):
            result += char
            # Add branch after 'F' if conditions met
            if char == 'F' and i < len(string) - 1:
                should_add = random.random() < branch_probability or branches_added < min_branches_to_add
                if should_add:
                    branch_type = random.choice([
                        "[+FX]", "[-FX]", "[/FX]", "[\\FX]",
                        "[+F][-F]", "[&F]", "[^F]"
                    ])
                    result += branch_type
                    branches_added += 1

        # Ensure minimum branches were added if string was long enough
        if len(string) > 10 and branches_added < min_branches_to_add:
             # Try adding one more branch somewhere if possible
            f_indices = [i for i, char in enumerate(result) if char == 'F']
            if f_indices:
                insert_pos = random.choice(f_indices) + 1
                branch_type = random.choice(["[+FX]", "[-FX]", "[&FX]", "[^FX]"])
                result = result[:insert_pos] + branch_type + result[insert_pos:]

        return result


    def get_vertices(self):
        """Převádí vygenerovaný řetězec na posloupnost vrcholů a barev pro vykreslení."""
        vertices = []
        colors = []
        normals = []

        stack = []
        position = np.array([0.0, 0.0, 0.0], dtype='f4') # Start at base
        direction = np.array([0.0, 1.0, 0.0], dtype='f4') # Initial direction up

        current_length = self.initial_length
        current_width = self.initial_width # Use the new property

        branch_depth = 0
        max_render_depth = 15 # Limit depth for color/width calculation, prevents extreme values

        # Helper to track segments and prevent straight lines without rotation/branching
        segments_since_turn_or_branch = 0


        for char in self.current_string:
            if char == 'F':
                start = position.copy()
                # Add slight random deviation to avoid perfectly straight lines over long segments
                if segments_since_turn_or_branch > 2:
                    dev_angle = random.uniform(-math.radians(3), math.radians(3))
                    dev_axis = random.choice(['x','y','z'])
                    if dev_axis == 'x': direction = self._rotate_x(direction, dev_angle)
                    elif dev_axis == 'y': direction = self._rotate_y(direction, dev_angle)
                    else: direction = self._rotate_z(direction, dev_angle)

                end = position + direction * current_length

                vertices.extend(start)
                vertices.extend(end)

                # Calculate color based on depth/width
                segment_color = self._compute_segment_color(branch_depth, max_render_depth, current_width)
                colors.extend(segment_color)
                colors.extend(segment_color)

                segment_normal = self._compute_normal(direction)
                normals.extend(segment_normal)
                normals.extend(segment_normal)

                position = end
                segments_since_turn_or_branch += 1

            elif char in '+-&^\\/': # Any rotation resets segment count
                segments_since_turn_or_branch = 0
                if char == '+': direction = self._rotate_y(direction, self.angle)
                elif char == '-': direction = self._rotate_y(direction, -self.angle)
                elif char == '&': direction = self._rotate_x(direction, self.angle)
                elif char == '^': direction = self._rotate_x(direction, -self.angle)
                elif char == '\\': direction = self._rotate_z(direction, self.angle)
                elif char == '/': direction = self._rotate_z(direction, -self.angle)

            elif char == '[':
                segments_since_turn_or_branch = 0
                # Push state: position, direction, length, width, depth
                stack.append((position.copy(), direction.copy(), current_length, current_width, branch_depth))
                # Apply scale to length and width for the new branch
                current_length *= self.scale
                current_width *= self.width_reduction_factor # Reduce width
                branch_depth += 1

            elif char == ']':
                segments_since_turn_or_branch = 0 # Reset count after returning from branch
                if stack:
                    # Pop state
                    position, direction, current_length, current_width, branch_depth = stack.pop()
                else:
                    logging.warning("Attempted to pop from an empty stack. L-system string might be malformed.")
                    # As a fallback, reset to some sensible defaults to avoid crashing
                    position = np.array([0.0, -0.5, 0.0], dtype='f4')
                    direction = np.array([0.0, 1.0, 0.0], dtype='f4')
                    current_length = self.initial_length
                    current_width = self.initial_width
                    branch_depth = 0


            elif char == 'X': # Represents a leaf or terminal point
                 # Draw a small segment for the leaf
                start = position.copy()

                # Randomize leaf direction slightly
                leaf_dir = direction.copy()
                rand_angle_x = random.uniform(-math.pi / 6, math.pi / 6)
                rand_angle_y = random.uniform(-math.pi / 6, math.pi / 6)
                leaf_dir = self._rotate_x(leaf_dir, rand_angle_x)
                leaf_dir = self._rotate_y(leaf_dir, rand_angle_y)

                # Leaf size can be related to current branch length, but keep it small
                leaf_size = max(current_length * 0.5, self.initial_length * 0.05) # Ensure minimum size
                end = position + leaf_dir * leaf_size

                vertices.extend(start)
                vertices.extend(end)

                # Transition color from branch to leaf
                transition_color = self._compute_leaf_transition_color(branch_depth, max_render_depth, current_width)
                colors.extend(transition_color)
                colors.extend(self.leaf_color) # End with leaf color

                leaf_normal = self._compute_normal(leaf_dir)
                normals.extend(leaf_normal)
                normals.extend(leaf_normal)

        if not vertices:
            logging.warning("No vertices generated from L-system string")
            return np.array([], dtype='f4'), np.array([], dtype='f4'), np.array([], dtype='f4')

        return np.array(vertices, dtype='f4'), np.array(colors, dtype='f4'), np.array(normals, dtype='f4')


    def _compute_segment_color(self, depth, max_depth, width):
        """Vypočítá barvu segmentu na základě hloubky větvení a aktuální šířky."""
        # Blend based on depth (0 = trunk color, 1 = lighter/leafier color)
        # Use clamped depth to avoid extreme values if max_depth is exceeded
        clamped_depth = min(depth, max_depth)
        depth_factor = clamped_depth / max_depth if max_depth > 0 else 0

        # Blend based on width (relative to initial width)
        width_factor = width / self.initial_width if self.initial_width > 0 else 0
        # Make thinner branches slightly brighter/yellower maybe
        width_color_shift = np.array([0.1, 0.1, -0.05], dtype='f4') * (1.0 - width_factor)

        # Interpolate between trunk and a slightly lighter/greener color based on depth
        # Target color shifts towards green as depth increases
        target_color = self.trunk_color + (self.leaf_color - self.trunk_color) * 0.3 # Target 30% towards leaf color
        base_color = self.trunk_color * (1.0 - depth_factor) + target_color * depth_factor

        # Apply width-based shift
        final_color = base_color + width_color_shift

        return np.clip(final_color, 0.0, 1.0)


    def _compute_leaf_transition_color(self, depth, max_depth, width):
        """Vypočítá přechodovou barvu mezi větví a listem."""
        # Get the color of the branch segment leading to the leaf
        branch_color = self._compute_segment_color(depth, max_depth, width)

        # Blend branch color towards leaf color (e.g., 50/50 mix for the transition point)
        transition_factor = 0.6 # How much leaf color influences the transition point
        color = branch_color * (1 - transition_factor) + self.leaf_color * transition_factor

        return np.clip(color, 0.0, 1.0)

    def _compute_normal(self, direction):
        """Vypočítá normálu kolmou na směr větve (robustnější verze)."""
        direction = direction / (np.linalg.norm(direction) + 1e-9) # Normalize direction first

        # Try cross product with world up vector
        up = np.array([0.0, 1.0, 0.0], dtype='f4')
        cross_up = np.cross(direction, up)
        norm_up = np.linalg.norm(cross_up)

        if norm_up > 1e-6:
            return cross_up / norm_up # Use normalized cross product with Up

        # If direction is parallel to Up, try cross product with world right vector
        right = np.array([1.0, 0.0, 0.0], dtype='f4')
        cross_right = np.cross(direction, right)
        norm_right = np.linalg.norm(cross_right)

        if norm_right > 1e-6:
            return cross_right / norm_right # Use normalized cross product with Right

        # If direction is also parallel to Right (shouldn't happen if dir != 0), use Forward
        forward = np.array([0.0, 0.0, 1.0], dtype='f4')
        return forward # Fallback, though shouldn't be needed with initial normalization


    def _rotate_y(self, v, angle):
        """Rotace vektoru kolem osy Y."""
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        # Corrected matrix application for numpy arrays
        x = v[0] * cos_a + v[2] * sin_a
        y = v[1]
        z = -v[0] * sin_a + v[2] * cos_a
        return np.array([x, y, z], dtype='f4')

    def _rotate_x(self, v, angle):
        """Rotace vektoru kolem osy X."""
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        x = v[0]
        y = v[1] * cos_a - v[2] * sin_a
        z = v[1] * sin_a + v[2] * cos_a
        return np.array([x, y, z], dtype='f4')

    def _rotate_z(self, v, angle):
        """Rotace vektoru kolem osy Z."""
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        x = v[0] * cos_a - v[1] * sin_a
        y = v[0] * sin_a + v[1] * cos_a
        z = v[2]
        return np.array([x, y, z], dtype='f4')
