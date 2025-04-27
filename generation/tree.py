import numpy as np
import math
import random
import logging

logger = logging.getLogger(__name__)

class Tree:
    def __init__(self, instructions: str, angle: float = 25.0, length: float = 0.1, branch_radius: float = 0.02, 
                 tree_type: str = "pine"):
        self.instructions = instructions
        self.angle = math.radians(angle)
        self.length = length
        self.branch_radius = branch_radius
        self.tree_type = tree_type
        self.growth_factor = 0.0  # For animation, 0.0 to 1.0
        self.vertices = None
        self.normals = None
        self.indices = None
        
        # Build the mesh
        self._build_mesh()

    def _build_mesh(self):
        """Build tree vertices and indices for rendering as triangles"""
        # First generate the branch endpoints
        branch_segments = self._generate_branch_segments()
    
    # Then convert these segments to 3D cylindrical branches
        vertices, normals, indices = self._create_cylindrical_branches(branch_segments)
    
        # Add leaf points based on tree type
        leaf_vertices, leaf_normals, leaf_indices = self._add_leaves(branch_segments)
    
    # Combine branch and leaf geometry
        if len(leaf_vertices) > 0:
        # Reshape vertices if they're 1D arrays
            if vertices.ndim == 1:
            # Assuming each vertex has 6 components (position + normal)
                vertices = vertices.reshape(-1, 6)
            if leaf_vertices.ndim == 1:
                leaf_vertices = leaf_vertices.reshape(-1, 6)
        
        # Now check shapes
            logger.debug(f"Branch vertices shape: {vertices.shape}")
            logger.debug(f"Leaf vertices shape: {leaf_vertices.shape}")
        
            if vertices.shape[1] != leaf_vertices.shape[1]:
                raise ValueError(
                    f"Cannot concatenate vertices with shapes {vertices.shape} and {leaf_vertices.shape}. "
                    "Branch and leaf vertex structures must match."
                )
        
        # Calculate offset for indices
            index_offset = vertices.shape[0]  # Number of vertices before adding leaves
        
        # Adjust leaf indices
            adjusted_leaf_indices = leaf_indices + index_offset
        
        # Combine arrays
            vertices = np.vstack([vertices, leaf_vertices])
            normals = np.vstack([normals, leaf_normals])
            indices = np.concatenate([indices, adjusted_leaf_indices])
    
    # Store final mesh data
        self.vertices = vertices
        self.normals = normals
        self.indices = indices    

    def _generate_branch_segments(self):
        """Generate the basic branch segments from L-system instructions"""
        stack = []
        pos = np.array([0.0, 0.0, 0.0], dtype='f4')  # Start at ground level
        dir = np.array([0.0, 1.0, 0.0], dtype='f4')
        
        # Track branch level for thickness
        branch_level = 0
        max_branch_level = 10  # Cap to prevent too thin branches
        
        segments = []
        thickness = 1.0  # Start with full thickness
        
        for c in self.instructions:
            if c == 'F':
                # Calculate new position with randomness based on tree type
                branch_length = self.length
                
                # Add tree-specific variations
                if self.tree_type == "pine":
                    # Pines have straighter branches
                    randomness = 0.05
                elif self.tree_type == "oak":
                    # Oaks have more variation
                    randomness = 0.2
                elif self.tree_type == "bush":
                    # Bushes are very variable
                    randomness = 0.3
                else:
                    randomness = 0.1
                    
                branch_length *= (1.0 - randomness + 2 * randomness * random.random())
                new_pos = pos + dir * branch_length
                
                # Store segment with thickness
                segments.append((pos.copy(), new_pos.copy(), thickness))
                pos = new_pos
                
            elif c == '+':
                # Apply rotation with tree-specific randomness
                if self.tree_type == "pine":
                    # Pines have more regular angles
                    rand_factor = 0.1
                else:
                    # Other trees have more variation
                    rand_factor = 0.3
                    
                theta = self.angle * (1.0 - rand_factor + 2 * rand_factor * random.random())
                rot = self._rotation_matrix(theta)
                dir = rot.dot(dir)
                dir = dir / np.linalg.norm(dir)
                
            elif c == '-':
                # Apply rotation with tree-specific randomness
                if self.tree_type == "pine":
                    # Pines have more regular angles
                    rand_factor = 0.1
                else:
                    # Other trees have more variation
                    rand_factor = 0.3
                    
                theta = -self.angle * (1.0 - rand_factor + 2 * rand_factor * random.random())
                rot = self._rotation_matrix(theta)
                dir = rot.dot(dir)
                dir = dir / np.linalg.norm(dir)
                
            elif c == '[':
                # Push current state onto stack and increase branch level
                stack.append((pos.copy(), dir.copy(), thickness))
                branch_level = min(branch_level + 1, max_branch_level)
                
                # Reduce thickness for new branch - different for each tree type
                if self.tree_type == "pine":
                    thickness *= 0.7  # Thinner branches for pines
                elif self.tree_type == "bush":
                    thickness *= 0.85  # Thicker branches for bushes
                else:
                    thickness *= 0.8  # Default
                
            elif c == ']':
                # Pop state from stack and decrease branch level
                if stack:
                    pos, dir, thickness = stack.pop()
                    branch_level = max(branch_level - 1, 0)
        
        return segments

    def _rotation_matrix(self, angle_deg):
        """Random rotation around a random axis"""
        angle = math.radians(angle_deg)
        axis = np.random.normal(size=3)
        axis /= np.linalg.norm(axis)
    
        x, y, z = axis
        cos = math.cos(angle)
        sin = math.sin(angle)
        C = 1 - cos
    
        return np.array([
            [cos + x*x*C,     x*y*C - z*sin, x*z*C + y*sin],
            [y*x*C + z*sin, cos + y*y*C,     y*z*C - x*sin],
            [z*x*C - y*sin, z*y*C + x*sin, cos + z*z*C]
        ], dtype='f4')
 

    def _create_cylindrical_branches(self, segments):
        """Convert branch segments to 3D cylinders"""
        vertices = []
        normals = []
        indices = []
        
        # Number of sides for branch cylinders
        sides = 6  # Hexagonal branches for performance
        
        vertex_count = 0
        
        # Process each branch segment
        for start_pos, end_pos, thickness in segments:
            # Calculate branch direction and length
            branch_dir = end_pos - start_pos
            branch_length = np.linalg.norm(branch_dir)
            if branch_length < 1e-6:
                continue  # Skip zero-length branches
                
            branch_dir = branch_dir / branch_length
            
            # Calculate a perpendicular vector for creating the cylinder
            perp = self._perpendicular_vector(branch_dir)
            perp = perp / np.linalg.norm(perp)
            
            # Create vertices around both ends of the cylinder
            for i in range(sides):
                angle = 2 * math.pi * i / sides
                
                # Calculate rotation of perpendicular vector
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)
                normal = perp * cos_angle + np.cross(branch_dir, perp) * sin_angle
                normal = normal / np.linalg.norm(normal)
                
                # Scale by thickness
                scaled_normal = normal * thickness * self.branch_radius
                
                # Add vertices at start and end with normals
                vertices.extend([start_pos[0] + scaled_normal[0], start_pos[1] + scaled_normal[1], 
                               start_pos[2] + scaled_normal[2], normal[0], normal[1], normal[2]])
                vertices.extend([end_pos[0] + scaled_normal[0], end_pos[1] + scaled_normal[1],
                               end_pos[2] + scaled_normal[2], normal[0], normal[1], normal[2]])
                
                # Add indices for triangles (two triangles per side)
                if i < sides - 1:
                    # First triangle
                    indices.extend([vertex_count + i*2, vertex_count + i*2 + 1, vertex_count + i*2 + 2])
                    # Second triangle
                    indices.extend([vertex_count + i*2 + 1, vertex_count + i*2 + 3, vertex_count + i*2 + 2])
                else:
                    # Connect back to first vertices
                    indices.extend([vertex_count + i*2, vertex_count + i*2 + 1, vertex_count])
                    indices.extend([vertex_count + i*2 + 1, vertex_count + 1, vertex_count])
            
            vertex_count += sides * 2
        
        return np.array(vertices, dtype='f4'), np.array(normals, dtype='f4'), np.array(indices, dtype='i4')

    def _add_leaves(self, segments):
        """Add leaves based on tree type"""
        vertices = []
        normals = []
        indices = []
        
        # Only add leaves at branch ends based on tree type
        if self.tree_type == "pine":
            self._add_pine_needles(segments, vertices, normals, indices)
        elif self.tree_type == "oak":
            self._add_oak_leaves(segments, vertices, normals, indices)
        elif self.tree_type == "bush":
            self._add_bush_leaves(segments, vertices, normals, indices)
        
        return np.array(vertices, dtype='f4'), np.array(normals, dtype='f4'), np.array(indices, dtype='i4')

    def _add_pine_needles(self, segments, vertices, normals, indices):
        """Add needle-like leaves for pine trees"""
        # For simplicity, we're just adding triangle clusters at branch ends
        vertex_count = len(vertices) // 6
        
        # Get branch ends (positions that are only end points)
        branch_ends = self._get_branch_ends(segments)
        
        for end_point, thickness in branch_ends:
            # Skip very thick branches (likely the trunk)
            if thickness > 0.5:
                continue
                
            # Add clusters of needles around the branch end
            needle_count = random.randint(3, 8)
            for _ in range(needle_count):
                # Random direction for the needle
                needle_dir = np.array([
                    random.uniform(-1.0, 1.0),
                    random.uniform(0.3, 1.0),  # Mostly upward
                    random.uniform(-1.0, 1.0)
                ], dtype='f4')
                needle_dir = needle_dir / np.linalg.norm(needle_dir)
                
                # Create a thin, long needle
                needle_length = random.uniform(0.05, 0.15)
                needle_width = random.uniform(0.01, 0.03)
                
                # Create a simple triangular needle
                tip = end_point + needle_dir * needle_length
                
                # Calculate perpendicular vector for width
                perp = self._perpendicular_vector(needle_dir)
                perp = perp / np.linalg.norm(perp) * needle_width
                
                # Calculate vertices for the triangular needle
                v1 = end_point + perp
                v2 = end_point - perp
                
                # Add vertices with normals
                normal = np.cross(perp, needle_dir)
                normal = normal / np.linalg.norm(normal)
                
                # Add vertices
                vertex_index = len(vertices) // 6
                vertices.extend([tip[0], tip[1], tip[2], normal[0], normal[1], normal[2]])
                vertices.extend([v1[0], v1[1], v1[2], normal[0], normal[1], normal[2]])
                vertices.extend([v2[0], v2[1], v2[2], normal[0], normal[1], normal[2]])
                
                # Add indices for the triangle
                indices.extend([vertex_index, vertex_index + 1, vertex_index + 2])

    def _add_oak_leaves(self, segments, vertices, normals, indices):
        """Add broader leaves for oak trees"""
        # For simplicity, we're adding flat leaf-like quads at branch ends
        branch_ends = self._get_branch_ends(segments)
        
        for end_point, thickness in branch_ends:
            # Skip very thick branches (likely the trunk)
            if thickness > 0.5:
                continue
                
            # Add clusters of leaves around the branch end
            leaf_count = random.randint(2, 5)
            for _ in range(leaf_count):
                # Random direction for the leaf
                leaf_dir = np.array([
                    random.uniform(-0.7, 0.7),
                    random.uniform(0.3, 1.0),  # Mostly upward
                    random.uniform(-0.7, 0.7)
                ], dtype='f4')
                leaf_dir = leaf_dir / np.linalg.norm(leaf_dir)
                
                # Create a broader leaf
                leaf_length = random.uniform(0.07, 0.15)
                leaf_width = random.uniform(0.05, 0.1)
                
                # Calculate leaf center
                leaf_center = end_point + leaf_dir * (leaf_length * 0.5)
                
                # Calculate perpendicular vector for width
                perp = self._perpendicular_vector(leaf_dir)
                perp = perp / np.linalg.norm(perp) * leaf_width
                
                # Calculate quad vertices
                v1 = leaf_center + perp - leaf_dir * (leaf_length * 0.5)
                v2 = leaf_center - perp - leaf_dir * (leaf_length * 0.5)
                v3 = leaf_center - perp + leaf_dir * (leaf_length * 0.5)
                v4 = leaf_center + perp + leaf_dir * (leaf_length * 0.5)
                
                # Add vertices with normals
                normal = np.cross(perp, leaf_dir)
                normal = normal / np.linalg.norm(normal)
                
                # Add vertices
                vertex_index = len(vertices) // 6
                vertices.extend([v1[0], v1[1], v1[2], normal[0], normal[1], normal[2]])
                vertices.extend([v2[0], v2[1], v2[2], normal[0], normal[1], normal[2]])
                vertices.extend([v3[0], v3[1], v3[2], normal[0], normal[1], normal[2]])
                vertices.extend([v4[0], v4[1], v4[2], normal[0], normal[1], normal[2]])
                
                # Add indices for two triangles forming the quad
                indices.extend([vertex_index, vertex_index + 1, vertex_index + 2])
                indices.extend([vertex_index, vertex_index + 2, vertex_index + 3])

    def _add_bush_leaves(self, segments, vertices, normals, indices):
        """Add dense, small leaves for bushes"""
        # Bushes have many small leaves densely packed
        branch_ends = self._get_branch_ends(segments)
        
        for end_point, thickness in branch_ends:
            # Bushes can have leaves on thicker branches too
            if thickness > 0.8:
                continue
                
            # Add clusters of leaves around the branch end
            leaf_count = random.randint(4, 8)  # More leaves for bushes
            for _ in range(leaf_count):
                # Random direction for the leaf
                leaf_dir = np.array([
                    random.uniform(-1.0, 1.0),
                    random.uniform(-0.2, 1.0),  # Can point slightly downward
                    random.uniform(-1.0, 1.0)
                ], dtype='f4')
                leaf_dir = leaf_dir / np.linalg.norm(leaf_dir)
                
                # Create a small leaf
                leaf_length = random.uniform(0.03, 0.08)
                leaf_width = random.uniform(0.02, 0.05)
                
                # Calculate leaf center
                leaf_center = end_point + leaf_dir * (leaf_length * 0.5)
                
                # Calculate perpendicular vector for width
                perp = self._perpendicular_vector(leaf_dir)
                perp = perp / np.linalg.norm(perp) * leaf_width
                
                # Calculate quad vertices
                v1 = leaf_center + perp - leaf_dir * (leaf_length * 0.5)
                v2 = leaf_center - perp - leaf_dir * (leaf_length * 0.5)
                v3 = leaf_center - perp + leaf_dir * (leaf_length * 0.5)
                v4 = leaf_center + perp + leaf_dir * (leaf_length * 0.5)
                
                # Add vertices with normals
                normal = np.cross(perp, leaf_dir)
                normal = normal / np.linalg.norm(normal)
                
                # Add vertices
                vertex_index = len(vertices) // 6
                vertices.extend([v1[0], v1[1], v1[2], normal[0], normal[1], normal[2]])
                vertices.extend([v2[0], v2[1], v2[2], normal[0], normal[1], normal[2]])
                vertices.extend([v3[0], v3[1], v3[2], normal[0], normal[1], normal[2]])
                vertices.extend([v4[0], v4[1], v4[2], normal[0], normal[1], normal[2]])
                
                # Add indices for two triangles forming the quad
                indices.extend([vertex_index, vertex_index + 1, vertex_index + 2])
                indices.extend([vertex_index, vertex_index + 2, vertex_index + 3])

    def _get_branch_ends(self, segments):
        """Find branch end points by identifying endpoints that aren't start points"""
        start_points = set()
        end_points = []
        
        for start, end, thickness in segments:
            start_tuple = tuple(start)
            end_tuple = tuple(end)
            start_points.add(start_tuple)
            end_points.append((end_tuple, thickness))
        
        # Return only true end points
        return [(np.array(end), thickness) for end, thickness in end_points 
                if tuple(end) not in start_points]

    def _perpendicular_vector(self, v):
        """Find a perpendicular vector to the given vector"""
        # We need any vector perpendicular to v
        if abs(v[0]) < abs(v[1]):
            if abs(v[0]) < abs(v[2]):
                return np.array([1.0, 0.0, 0.0], dtype='f4')
            else:
                return np.array([0.0, 0.0, 1.0], dtype='f4')
        else:
            if abs(v[1]) < abs(v[2]):
                return np.array([0.0, 1.0, 0.0], dtype='f4')
            else:
                return np.array([0.0, 0.0, 1.0], dtype='f4')
        
    def set_growth(self, factor):
        """Set the growth factor for animation (0.0 to 1.0)"""
        self.growth_factor = max(0.0, min(1.0, factor))
        
    def get_growth_vertices(self):
        """Get vertices with growth factor applied"""
        if self.growth_factor >= 1.0:
            return self.vertices, self.normals, self.indices
            
        # For simplicity, we'll just scale the y-coordinate based on growth factor
        grown_vertices = self.vertices.copy()
        
        # Scale y values (height)
        for i in range(1, len(grown_vertices), 6):  # y is at index 1, 7, 13, etc.
            original_y = self.vertices[i]
            grown_vertices[i] = original_y * self.growth_factor
            
        return grown_vertices, self.normals, self.indices

    def create_ground_plane(self, size=5.0, y_position=-0.01):
        """Create a simple square ground plane"""
        # Create a simple quad for the ground
        vertices = np.array([
            # Position (XYZ) + Normal (XYZ)
            -size, y_position, -size, 0.0, 1.0, 0.0,
             size, y_position, -size, 0.0, 1.0, 0.0,
             size, y_position,  size, 0.0, 1.0, 0.0,
            -size, y_position,  size, 0.0, 1.0, 0.0
        ], dtype='f4')
        
        # Two triangles for the quad
        indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')
        
        # Normals all point up
        normals = np.array([
            0.0, 1.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 1.0, 0.0
        ], dtype='f4')
        
        return vertices, normals, indices
