# engine/camera.py
from pyrr import Matrix44, Vector3

class Camera:
    """Třída pro správu kamery a jejích matic."""
    def __init__(self, width, height, fov=45.0, near=0.1, far=100.0):
        self.aspect_ratio = width / height
        self.fov = fov
        self.near = near
        self.far = far

        self.position = Vector3([0.0, 0.0, 3.0]) # Posunuta dozadu
        self.target = Vector3([0.0, 0.5, 0.0])   # Míří na střed
        self.up = Vector3([0.0, 1.0, 0.0])       # Y osa je nahoru
        self.down = Vector3([0.0, -1.0, 0.0])
        self.back = Vector3([0.0, 0.0, 1.0])
        self.front = Vector3([0.0, 0.0, -1.0])
        self.right = Vector3([1.0, 0.0, 0.0])
        self.left = Vector3([-1.0, 0.0, 0.0])

        self.view_matrix = Matrix44.identity()
        self.projection_matrix = Matrix44.identity()

        self.update_projection_matrix()
        self.update_view_matrix()

    def update_view_matrix(self):
        """Aktualizuje pohledovou matici."""
        self.view_matrix = Matrix44.look_at(self.position, self.target, self.up)

    def update_projection_matrix(self):
        """Aktualizuje projekční matici."""
        self.projection_matrix = Matrix44.perspective_projection(
            self.fov, self.aspect_ratio, self.near, self.far
        )

    def get_view_matrix_bytes(self):
        """Vrátí pohledovou matici jako byty."""
        return self.view_matrix.astype('f4').tobytes()

    def get_projection_matrix_bytes(self):
        """Vrátí projekční matici jako byty."""
        return self.projection_matrix.astype('f4').tobytes()
