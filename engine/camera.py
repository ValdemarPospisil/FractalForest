from pyrr import Matrix44, Vector3
import numpy as np

class Camera:
    """Třída pro správu kamery a jejích matic."""
    def __init__(self, width, height, fov=45.0, near=0.1, far=100.0):
        self.aspect_ratio = width / height
        self.fov = fov
        self.near = near
        self.far = far

        self.position = Vector3([0.0, 0.0, 3.0])  # Posunuta dozadu
        self.target = Vector3([0.0, 0.5, 0.0])    # Míří na střed
        
        # Základní směrové vektory
        self.up = Vector3([0.0, 1.0, 0.0])        # Y osa je nahoru
        self.down = Vector3([0.0, -1.0, 0.0])
        self.back = Vector3([0.0, 0.0, 1.0])
        self.front = Vector3([0.0, 0.0, -1.0])
        self.right = Vector3([1.0, 0.0, 0.0])
        self.left = Vector3([-1.0, 0.0, 0.0])
        
        # Vektor, který udává směr pohledu kamery (od position k target)
        self.direction = self.target - self.position
        
        self.view_matrix = Matrix44.identity()
        self.projection_matrix = Matrix44.identity()

        self.update_projection_matrix()
        self.update_view_matrix()

    def update_view_matrix(self):
        """Aktualizuje pohledovou matici."""
        self.view_matrix = Matrix44.look_at(self.position, self.target, self.up)
        # Aktualizujeme směrový vektor
        self.direction = self.target - self.position
        self.direction = self.direction / np.linalg.norm(self.direction)
        
        # Aktualizujeme ostatní směrové vektory
        # Right vektor je kolmý na direction a up
        self.right = np.cross(self.direction, self.up)
        if np.linalg.norm(self.right) > 0:
            self.right = self.right / np.linalg.norm(self.right)
        
        # Skutečný up vektor (kolmý na right a direction)
        self.up = np.cross(self.right, self.direction)
        self.up = self.up / np.linalg.norm(self.up)
        
        # Odvození ostatních směrových vektorů
        self.left = -self.right
        self.front = self.direction  # Front je stejný jako direction
        self.back = -self.direction
        self.down = -self.up

    def update_projection_matrix(self):
        """Aktualizuje projekční matici."""
        self.projection_matrix = Matrix44.perspective_projection(
            self.fov, self.aspect_ratio, self.near, self.far
        )

    def move(self, direction_vector, distance):
        """Posune kameru a její cíl ve směru vektoru."""
        movement = direction_vector * distance
        self.position += movement
        self.target += movement
        self.update_view_matrix()
        
    def move_forward(self, distance):
        """Posune kameru dopředu."""
        self.position += self.front * distance
        self.target += self.front * distance
        self.update_view_matrix()
        
    def move_backward(self, distance):
        """Posune kameru dozadu."""
        self.position += self.back * distance
        self.target += self.back * distance
        self.update_view_matrix()
        
    def get_view_matrix_bytes(self):
        """Vrátí pohledovou matici jako byty."""
        return self.view_matrix.astype('f4').tobytes()

    def get_projection_matrix_bytes(self):
        """Vrátí projekční matici jako byty."""
        return self.projection_matrix.astype('f4').tobytes()
