import numpy as np
import math
import random

class Tree:
    def __init__(self, instructions: str, angle: float = 25.0, length: float = 0.1):
        self.instructions = instructions
        self.angle = math.radians(angle)
        self.length = length
        self.vertices = self._build_vertices()

    def _build_vertices(self) -> np.ndarray:
        """Build tree vertices with improved visualization"""
        stack = []
        pos = np.array([0.0, -1.0, 0.0], dtype='f4')
        dir = np.array([0.0, 1.0, 0.0], dtype='f4')
        
        # Track branch level for thickness
        branch_level = 0
        max_branch_level = 10  # Cap to prevent too thin branches
        
        vertices = []
        branch_thickness = 1.0  # Start with full thickness
        
        for c in self.instructions:
            if c == 'F':
                # Calculate new position
                branch_length = self.length * (0.95 + 0.1 * random.random())  # Slight randomness in length
                new_pos = pos + dir * branch_length
                
                # Add vertices with current thickness
                vertices.extend([pos.copy(), new_pos.copy()])
                pos = new_pos
                
            elif c == '+':
                # Apply rotation with slight randomness
                theta = self.angle * (0.9 + 0.2 * random.random())
                rot = np.array([
                    [math.cos(theta), -math.sin(theta), 0.0],
                    [math.sin(theta), math.cos(theta), 0.0],
                    [0.0, 0.0, 1.0]
                ], dtype='f4')
                dir = rot.dot(dir)
                # Normalize direction vector to prevent drift
                dir = dir / np.linalg.norm(dir)
                
            elif c == '-':
                # Apply rotation with slight randomness
                theta = -self.angle * (0.9 + 0.2 * random.random())
                rot = np.array([
                    [math.cos(theta), -math.sin(theta), 0.0],
                    [math.sin(theta), math.cos(theta), 0.0],
                    [0.0, 0.0, 1.0]
                ], dtype='f4')
                dir = rot.dot(dir)
                # Normalize direction vector to prevent drift
                dir = dir / np.linalg.norm(dir)
                
            elif c == '[':
                # Push current state onto stack and increase branch level
                stack.append((pos.copy(), dir.copy(), branch_thickness))
                branch_level = min(branch_level + 1, max_branch_level)
                # Reduce thickness for new branch
                branch_thickness *= 0.8
                
            elif c == ']':
                # Pop state from stack and decrease branch level
                pos, dir, branch_thickness = stack.pop()
                branch_level = max(branch_level - 1, 0)
                
        return np.array(vertices, dtype='f4')
        
    def add_leaves(self, leaf_density=0.3):
        """Add leaves to the tree (positions where leaves would be)"""
        # This could be expanded to actually add leaf geometry
        # For now we just return points where leaves could be placed
        leaf_positions = []
        
        # Find branch ends (positions that are only start points but not end points)
        branch_ends = set()
        for i in range(0, len(self.vertices), 2):
            if i+1 < len(self.vertices):
                end_point = tuple(self.vertices[i+1])
                branch_ends.add(end_point)
                
        # Convert to numpy array
        return np.array(list(branch_ends), dtype='f4')
