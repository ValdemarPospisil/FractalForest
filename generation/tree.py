import numpy as np
import math

class Tree:
    def __init__(self, instructions: str, angle: float = 25.0, length: float = 0.1):
        self.instructions = instructions
        self.angle = math.radians(angle)
        self.length = length
        self.vertices = self._build_vertices()

    def _build_vertices(self) -> np.ndarray:
        stack = []
        pos = np.array([0.0, -1.0, 0.0], dtype='f4')
        dir = np.array([0.0, 1.0, 0.0], dtype='f4')
        vertices = []
        for c in self.instructions:
            if c == 'F':
                new_pos = pos + dir * self.length
                vertices.extend([pos.copy(), new_pos.copy()])
                pos = new_pos
            elif c == '+':
                theta = self.angle
                rot = np.array([
                    [math.cos(theta), -math.sin(theta), 0.0],
                    [math.sin(theta), math.cos(theta), 0.0],
                    [0.0, 0.0, 1.0]
                ], dtype='f4')
                dir = rot.dot(dir)
            elif c == '-':
                theta = -self.angle
                rot = np.array([
                    [math.cos(theta), -math.sin(theta), 0.0],
                    [math.sin(theta), math.cos(theta), 0.0],
                    [0.0, 0.0, 1.0]
                ], dtype='f4')
                dir = rot.dot(dir)
            elif c == '[':
                stack.append((pos.copy(), dir.copy()))
            elif c == ']':
                pos, dir = stack.pop()
        return np.array(vertices, dtype='f4')
